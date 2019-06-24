import logging
import os
import json
import libghdl
import libghdl.thin.errorout_memory as errorout_memory
import libghdl.thin.flags
import libghdl.thin.errorout as errorout
import libghdl.thin.files_map as files_map
import libghdl.thin.libraries as libraries
import libghdl.thin.name_table as name_table
import libghdl.thin.vhdl.nodes as nodes
import libghdl.thin.vhdl.std_package as std_package
import libghdl.thin.vhdl.parse
import libghdl.thin.vhdl.pyutils as pyutils

from . import lsp
from . import document, symbols

log = logging.getLogger(__name__)

class Workspace(object):

    M_PUBLISH_DIAGNOSTICS = 'textDocument/publishDiagnostics'
    M_APPLY_EDIT = 'workspace/applyEdit'
    M_SHOW_MESSAGE = 'window/showMessage'

    def __init__(self, root_uri, server):
        self._root_uri = root_uri
        self._server = server
        self._root_path = lsp.path_from_uri(self._root_uri)
        self._docs = {}     # uri -> doc
        self._fe_map = {}   # fe -> doc
        self._prj = {}
        errorout_memory.Install_Handler()
        libghdl.thin.flags.Flag_Elocations.value = True
        #thin.Flags.Verbose.value = True
        # We do analysis even in case of errors.
        libghdl.thin.vhdl.parse.Flag_Parse_Parenthesis.value = True
        # Force analysis to get more feedback + navigation even in case
        # of errors.
        libghdl.thin.flags.Flag_Force_Analysis.value = True
        # Do not consider analysis order issues.
        libghdl.thin.flags.Flag_Elaborate_With_Outdated.value = True
        libghdl.thin.errorout.Enable_Warning(errorout.Msgid.Warnid_Unused, True)
        self.read_project()
        self.set_options_from_project()
        libghdl.analyze_init()
        self._diags_set = set() # Documents with at least one diagnostic.
        self.read_files_from_project()
        self.gather_diagnostics(None)

    @property
    def documents(self):
        return self._docs

    @property
    def root_path(self):
        return self._root_path

    @property
    def root_uri(self):
        return self._root_uri

    def create_document_from_sfe(self, sfe, abspath):
        doc_uri = 'file://' + os.path.normpath(abspath)
        doc = document.Document(doc_uri, sfe)
        self._fe_map[sfe] = doc
        self._docs[doc_uri] = doc
        return doc

    def sfe_to_document(self, sfe):
        """Get the document correspond to :param sfe: source file.
        Can create the document if needed."""
        assert sfe != 0
        doc = self._fe_map.get(sfe, None)
        if doc is None:
            # Could be a document from outside...
            filename = pyutils.name_image(files_map.Get_File_Name(sfe))
            if not os.path.isabs(filename):
                dirname = pyutils.name_image(files_map.Get_Directory_Name(sfe))
                filename = os.path.join(dirname, filename)
            doc = self.create_document_from_sfe(sfe, filename)
        return doc

    def add_vhdl_file(self, name):
        log.info("loading %s", name)
        if os.path.isabs(name):
            absname = name
        else:
            absname = os.path.join(self._root_path, name)
        # Create a document for this file.
        sfe = document.Document.load(open(absname).read(), self._root_path, name)
        doc = self.create_document_from_sfe(sfe, absname)
        doc._tree = document.Document.parse_document(sfe)
        if doc._tree != nodes.Null_Iir:
            doc._tree = document.Document.add_to_library(doc._tree)

    def read_project(self):
        prj_file = os.path.join(self.root_path, 'hdl-prj.json')
        if not os.path.exists(prj_file):
            log.info("project file %s not found", prj_file)
            return
        try:
            with open(prj_file) as f:
                log.info("reading project file %s", prj_file)
                self._prj = json.load(f)
        except json.decoder.JSONDecodeError as e:
            log.info("error in project file")
            self._server.show_message(
                lsp.MessageType.Error,
                "json error in project file {}:{}:{}".format(
                    prj_file, e.lineno, e.colno)
            )

    def set_options_from_project(self):
        if self._prj is None:
            return
        if not isinstance(self._prj, dict):
            log.error("project file is not a dictionnary")
            return
        opts = self._prj.get('options', None)
        if opts is None:
            return
        if not isinstance(opts, dict):
            log.error("'options' is not a dictionnary")
            return
        ghdl_opts = opts.get('ghdl_analysis', None)
        if ghdl_opts is None:
            return
        log.info("Using options: %s", ghdl_opts)
        for opt in ghdl_opts:
            libghdl.set_option(opt.encode('utf-8'))

    def read_files_from_project(self):
        files = self._prj.get('files', [])
        if not isinstance(files, list):
            log.error("'files' is not a list")
            return
        for f in files:
            if not isinstance(f, dict):
                log.error("an element of 'files' is not a dict")
                return
            name = f.get('file')
            if not isinstance(name, str):
                log.error("a 'file' is not a string")
                return
            lang = f.get('language', 'vhdl')
            if lang == 'vhdl':
                self.add_vhdl_file(name)

    def _create_document(self, doc_uri, source=None, version=None):
        path = lsp.path_from_uri(doc_uri)
        if source is None:
            source = open(path).read()
        sfe = document.Document.load(source, os.path.dirname(path), os.path.basename(path))
        return document.Document(doc_uri, sfe, version)

    def get_or_create_document(self, doc_uri):
        return self._docs.get(doc_uri) or self._create_document(doc_uri)

    def get_document(self, doc_uri):
        return self._docs.get(doc_uri)

    def put_document(self, doc_uri, source, version=None):
        doc = self.get_document(doc_uri)
        if doc is None:
            doc = self._create_document(doc_uri, source=source, version=version)
            self._docs[doc_uri] = doc
            if doc._fe is not None:
                self._fe_map[doc._fe] = doc
        else:
            # The document may already be present (loaded from a project)
            # In that case, overwrite it as the client may have a more
            # recent version.
            doc.reload(source)
        return doc

    def get_configuration(self):
        self._server.configuration([{'scopeUri': '', 'section': 'vhdl.maxNumberOfProblems'}])

    def gather_diagnostics(self, doc):
        # Gather messages (per file)
        nbr_msgs = errorout_memory.Get_Nbr_Messages()
        diags = {}
        diag = {}
        for i in range(nbr_msgs):
            hdr = errorout_memory.Get_Error_Record(i+1)
            msg = errorout_memory.Get_Error_Message(i+1).decode('utf-8')
            if hdr.file == 0:
                # Possible for error limit reached.
                continue
            err_range = {
                'start': {'line': hdr.line - 1, 'character': hdr.offset},
                'end': {'line': hdr.line - 1,
                        'character': hdr.offset + hdr.length},
            }
            if hdr.group <= errorout_memory.Msg_Main:
                if hdr.id <= errorout.Msgid.Msgid_Note:
                    severity = lsp.DiagnosticSeverity.Information
                elif hdr.id <= errorout.Msgid.Msgid_Warning:
                    severity = lsp.DiagnosticSeverity.Warning
                else:
                    severity = lsp.DiagnosticSeverity.Error
                diag = {'source': 'ghdl',
                        'range': err_range,
                        'message': msg,
                        'severity': severity}
                if hdr.group == errorout_memory.Msg_Main:
                    diag['relatedInformation'] = []
                fdiag = diags.get(hdr.file, None)
                if fdiag is None:
                    diags[hdr.file] = [diag]
                else:
                    fdiag.append(diag)
            else:
                assert diag
                if True:
                    doc = self.sfe_to_document(hdr.file)
                    diag['relatedInformation'].append(
                        {'location': {'uri': doc.uri, 'range': err_range},
                         'message': msg})
        errorout_memory.Clear_Errors()
        # Publish diagnostics
        for sfe, diag in diags.items():
            doc = self.sfe_to_document(sfe)
            self.publish_diagnostics(doc.uri, diag)
        if doc is not None and doc._fe not in diags:
            # Clear previous diagnostics for the doc.
            self.publish_diagnostics(doc.uri, [])

    def lint(self, doc_uri):
        d = self.get_document(doc_uri)
        d.compute_diags()
        self.gather_diagnostics(d)

    def check_document(self, doc_uri, source):
        self._docs[doc_uri].check_document(source)

    def rm_document(self, doc_uri):
        pass

    def apply_edit(self, edit):
        return self._server.request(self.M_APPLY_EDIT, {'edit': edit})

    def publish_diagnostics(self, doc_uri, diagnostics):
        self._server.notify(self.M_PUBLISH_DIAGNOSTICS, params={'uri': doc_uri, 'diagnostics': diagnostics})

    def show_message(self, message, msg_type=lsp.MessageType.Info):
        self._server.notify(self.M_SHOW_MESSAGE, params={'type': msg_type, 'message': message})

    def declaration_to_location(self, decl):
        "Convert declaration :param decl: to an LSP Location"
        decl_loc = nodes.Get_Location(decl)
        if decl_loc == std_package.Std_Location.value:
            # There is no real file for the std.standard package.
            return None
        if decl_loc == libraries.Library_Location.value:
            # Libraries declaration are virtual.
            return None
        fe = files_map.Location_To_File(decl_loc)
        doc = self.sfe_to_document(fe)
        res = {'uri': doc.uri}
        nid = nodes.Get_Identifier(decl)
        res['range'] = {'start': symbols.location_to_position(fe, decl_loc),
                        'end': symbols.location_to_position(fe, decl_loc + name_table.Get_Name_Length(nid))}
        return res

    def goto_definition(self, doc_uri, position):
        decl = self._docs[doc_uri].goto_definition(position)
        if decl is None:
            return None
        decl_loc = self.declaration_to_location(decl)
        if decl_loc is None:
            return None
        res = [decl_loc]
        if nodes.Get_Kind(decl) == nodes.Iir_Kind.Component_Declaration:
            ent = libraries.Find_Entity_For_Component(nodes.Get_Identifier(decl))
            if ent != nodes.Null_Iir:
                res.append(self.declaration_to_location(nodes.Get_Library_Unit(ent)))
        return res

    def x_show_all_files(self):
        res = []
        for fe in range(1, files_map.Get_Last_Source_File_Entry() + 1):
            doc = self._fe_map.get(fe, None)
            res.append({'fe': fe,
                        'uri': doc.uri if doc is not None else None,
                        'name': pyutils.name_image(files_map.Get_File_Name(fe)),
                        'dir': pyutils.name_image(files_map.Get_Directory_Name(fe))})
        return res

    def x_get_all_entities(self):
        res = []
        lib = libraries.Get_Libraries_Chain()
        while lib != nodes.Null_Iir:
            files = nodes.Get_Design_File_Chain(lib)
            ents = []
            while files != nodes.Null_Iir:
                units = nodes.Get_First_Design_Unit(files)
                while units != nodes.Null_Iir:
                    unitlib = nodes.Get_Library_Unit(units)
                    if nodes.Get_Kind(unitlib) == nodes.Iir_Kind.Entity_Declaration:
                        ents.append(unitlib)
                    units = nodes.Get_Chain(units)
                files = nodes.Get_Chain(files)
            ents = [pyutils.name_image(nodes.Get_Identifier(e)) for e in ents]
            lib_name = pyutils.name_image(nodes.Get_Identifier(lib))
            res.extend([{'name': n, 'library': lib_name} for n in ents])
            lib = nodes.Get_Chain(lib)
        return res


