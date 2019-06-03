Content-Length: 2167

{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"processId":11082,"rootPath":"/home/tgingold/work/vhdl-language-server/tests/002coverage","rootUri":"file:///home/tgingold/work/vhdl-language-server/tests/002coverage","capabilities":{"workspace":{"applyEdit":true,"workspaceEdit":{"documentChanges":true},"didChangeConfiguration":{"dynamicRegistration":true},"didChangeWatchedFiles":{"dynamicRegistration":true},"symbol":{"dynamicRegistration":true,"symbolKind":{"valueSet":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]}},"executeCommand":{"dynamicRegistration":true},"configuration":true,"workspaceFolders":true},"textDocument":{"publishDiagnostics":{"relatedInformation":true},"synchronization":{"dynamicRegistration":true,"willSave":true,"willSaveWaitUntil":true,"didSave":true},"completion":{"dynamicRegistration":true,"contextSupport":true,"completionItem":{"snippetSupport":true,"commitCharactersSupport":true,"documentationFormat":["markdown","plaintext"],"deprecatedSupport":true},"completionItemKind":{"valueSet":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]}},"hover":{"dynamicRegistration":true,"contentFormat":["markdown","plaintext"]},"signatureHelp":{"dynamicRegistration":true,"signatureInformation":{"documentationFormat":["markdown","plaintext"]}},"definition":{"dynamicRegistration":true},"references":{"dynamicRegistration":true},"documentHighlight":{"dynamicRegistration":true},"documentSymbol":{"dynamicRegistration":true,"symbolKind":{"valueSet":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]}},"codeAction":{"dynamicRegistration":true},"codeLens":{"dynamicRegistration":true},"formatting":{"dynamicRegistration":true},"rangeFormatting":{"dynamicRegistration":true},"onTypeFormatting":{"dynamicRegistration":true},"rename":{"dynamicRegistration":true},"documentLink":{"dynamicRegistration":true},"typeDefinition":{"dynamicRegistration":true},"implementation":{"dynamicRegistration":true},"colorProvider":{"dynamicRegistration":true}}},"trace":"off","workspaceFolders":[{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/002coverage","name":"002coverage"}]}}Content-Length: 52

{"jsonrpc":"2.0","method":"initialized","params":{}}Content-Length: 665

{"jsonrpc":"2.0","method":"textDocument/didOpen","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","languageId":"vhdl","version":1,"text":"\nentity adder is\n  -- `i0`, `i1`, and the carry-in `ci` are inputs of the adder.\n  -- `s` is the sum output, `co` is the carry-out.\n  port (i0, i1 : in bit; ci : in bit; s : out bit; co : out bit);\nend adder;\n\narchitecture rtl of adder is\nbegin\n  --  This full-adder architecture contains two concurrent assignments.\n  --  Compute the sum.\n  s <= i0 xor i1 xor ci;\n  --  Compute the carry.\n  co <= (i0 and i1) or (i0 and ci) or (i1 and ci);\nend rtl;\n\n"}}}Content-Length: 170

{"jsonrpc":"2.0","id":1,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl"}}}Content-Length: 2026

{"jsonrpc":"2.0","method":"textDocument/didOpen","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder_tb.vhdl","languageId":"vhdl","version":1,"text":"\n--  A testbench has no ports.\nentity adder_tb is\nend adder_tb;\n\narchitecture behav of adder_tb is\n  --  Declaration of the component that will be instantiated.\n  component adder\n    port (i0, i1 : in bit; ci : in bit; s : out bit; co : out bit);\n  end component;\n\n  --  Specifies which entity is bound with the component.\n  for adder_0: adder use entity work.adder;\n  signal i0, i1, ci, s, co : bit;\nbegin\n  --  Component instantiation.\n  adder_0: adder port map (i0 => i0, i1 => i1, ci => ci,\n                           s => s, co => co);\n\n  --  This process does the real job.\n  process\n    type pattern_type is record\n      --  The inputs of the adder.\n      i0, i1, ci : bit;\n      --  The expected outputs of the adder.\n      s, co : bit;\n    end record;\n    --  The patterns to apply.\n    type pattern_array is array (natural range <>) of pattern_type;\n    constant patterns : pattern_array :=\n      (('0', '0', '0', '0', '0'),\n       ('0', '0', '1', '1', '0'),\n       ('0', '1', '0', '1', '0'),\n       ('0', '1', '1', '0', '1'),\n       ('1', '0', '0', '1', '0'),\n       ('1', '0', '1', '0', '1'),\n       ('1', '1', '0', '0', '1'),\n       ('1', '1', '1', '1', '1'));\n  begin\n    --  Check each pattern.\n    for i in patterns'range loop\n      --  Set the inputs.\n      i0 <= patterns(i).i0;\n      i1 <= patterns(i).i1;\n      ci <= patterns(i).ci;\n      --  Wait for the results.\n      wait for 1 ns;\n      --  Check the outputs.\n      assert s = patterns(i).s\n        report \"bad sum value\" severity error;\n      assert co = patterns(i).co\n        report \"bad carry out value\" severity error;\n    end loop;\n    assert false report \"end of test\" severity note;\n    --  Wait forever; this will finish the simulation.\n    wait;\n  end process;\nend behav;\n\n\n"}}}Content-Length: 173

{"jsonrpc":"2.0","id":2,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder_tb.vhdl"}}}Content-Length: 207

{"jsonrpc":"2.0","id":3,"method":"textDocument/definition","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder_tb.vhdl"},"position":{"line":12,"character":39}}}Content-Length: 299

{"jsonrpc":"2.0","method":"textDocument/didChange","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","version":2},"contentChanges":[{"range":{"start":{"line":11,"character":24},"end":{"line":11,"character":24}},"rangeLength":0,"text":"\n  "}]}}Content-Length: 170

{"jsonrpc":"2.0","id":4,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl"}}}Content-Length: 294

{"jsonrpc":"2.0","method":"textDocument/didChange","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","version":3},"contentChanges":[{"range":{"start":{"line":12,"character":2},"end":{"line":12,"character":2}},"rangeLength":0,"text":"e"}]}}Content-Length: 170

{"jsonrpc":"2.0","id":5,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl"}}}Content-Length: 294

{"jsonrpc":"2.0","method":"textDocument/didChange","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","version":4},"contentChanges":[{"range":{"start":{"line":12,"character":3},"end":{"line":12,"character":3}},"rangeLength":0,"text":"r"}]}}Content-Length: 294

{"jsonrpc":"2.0","method":"textDocument/didChange","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","version":5},"contentChanges":[{"range":{"start":{"line":12,"character":4},"end":{"line":12,"character":4}},"rangeLength":0,"text":"r"}]}}Content-Length: 170

{"jsonrpc":"2.0","id":6,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl"}}}Content-Length: 294

{"jsonrpc":"2.0","method":"textDocument/didChange","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","version":6},"contentChanges":[{"range":{"start":{"line":12,"character":5},"end":{"line":12,"character":5}},"rangeLength":0,"text":";"}]}}Content-Length: 170

{"jsonrpc":"2.0","id":7,"method":"textDocument/documentSymbol","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl"}}}Content-Length: 293

{"jsonrpc":"2.0","method":"textDocument/didChange","params":{"textDocument":{"uri":"file:///home/tgingold/work/vhdl-language-server/tests/files/adder.vhdl","version":7},"contentChanges":[{"range":{"start":{"line":12,"character":2},"end":{"line":13,"character":2}},"rangeLength":7,"text":""}]}}