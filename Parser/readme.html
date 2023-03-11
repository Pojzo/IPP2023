<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ipp_documentation.pdf</title>
  <link rel="stylesheet" href="https://stackedit.io/style.css" />
</head>

<body class="stackedit">
  <div class="stackedit__html"><p>Implementační dokumentace k 1. úloze do IPP 2022/2023</p>
<p>Jméno a příjmení: Peter Kováč</p>
<p>Login: xkovac66</p>
<h1 id="file-structure">File structure</h1>
<p>To make the implementation more concise, the source code was split into multiple files, each with their own respective classes.</p>
<ul>
<li>Files
<ul>
<li><em>parse.php</em></li>
<li><em>input_handler.php</em> - <code>class InputHandler()</code></li>
<li><em>analyzer.php</em> - <code>class Analyzer()</code></li>
<li><em>generator.php</em>: <code>class XMLGenerator()</code>, <code>class MyXMLWriter()</code></li>
</ul>
</li>
</ul>
<h1 id="implementation">Implementation</h1>
<h2 id="handling-input">Handling input</h2>
<p>When the program is run, the raw input from stdin is loaded by the <strong>Input Handler</strong> class, more precisely the <code>load_instructions</code> function, which checks for correctness of the <em>header</em>, removes comments and rids the lines of any unnecesasry whitespace. It then returns an array of <em>$lines</em> to the main program <em>parse.php</em> for further analysis.</p>
<h2 id="lexical-and-syntax-analysis">Lexical and syntax analysis</h2>
<p>The analysis  is performed in <strong>Analyzer</strong> class by the <code>analyze()</code> function, which calls the <code>instruction_ok(string $instruction)</code> function for each line in the $lines array. <code>instruction_ok()</code> extracts the <em>opcode</em>, check if if it’s valid and whether the instruction has the correct number fo arguments. The arguments are then passed to <code>check_syntax(\$instruction_arguments, $expected arguments)</code> function to verify their syntax. Regular expression along with some built-in <em>php</em> functions are used to validate the arguments. The functions used include: <code>is_string()</code>, <code>is_int()</code>, <code>is_bool()</code>, <code>is_type()</code>, <code>is_identifier()</code>.</p>
<h2 id="generating-output">Generating output</h2>
<p><strong>SimpleXML</strong> library is utilized to generate the XML output.<br>
The process is handled by the <code>generate_xml()</code> function in the <strong>XMLGenerator</strong> class, which takes the <code>$lines</code> array and generates the XML output line by line, or rather instruction after instruction.</p>
<p>At first, the <em>header</em> along with the mandatory <em>program</em> tag are generated. <em>$header</em> is created as a private member of the <strong>XMLGenerator</strong> object.</p>
<p>The <code>generate_instruction_xml()</code> function is used to create the <em>xml</em> representation of an instruction, where <em>order</em> and <em>opcode</em> attributes are added Every instruction is added as a child to the <em>$header</em>.  For each argument, function <code>generate_arg_xml()</code> function is called. Depending on the specific type of argument, functions <code>generate_variable_arg_xml()</code>, <code>generate_symbol_arg_xml()</code>, <code>generate_type_arg_xml()</code> and <code>generate_label_arg_xml()</code> functions are used.</p>
</div>
</body>

</html>
