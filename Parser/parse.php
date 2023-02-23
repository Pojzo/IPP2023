<?php

define("VARIABLE", 0);
define("SYMBOL", 1);
define("TYPE", 2);
define("LABEL", 3);


// dictionary mappings where key is the name of instruction and value is an array of arguments to that instruction
$instructions_dic = ["MOVE"    => [VARIABLE, SYMBOL],
    "CREATEFRAME" => [],
    "PUSHFRAME"   => [],
    "POPFRAME"    => [],
    "DEFVAR"      => [VARIABLE],
    "CALL"        => [LABEL],
    "RETURN"      => [],
    "PUSHS"       => [SYMBOL],
    "POPS"        => [VARIABLE],
    "ADD"         => [VARIABLE, SYMBOL, SYMBOL],
    "SUB"         => [VARIABLE, SYMBOL, SYMBOL],
    "MUL"         => [VARIABLE, SYMBOL, SYMBOL],
    "IDIV"        => [VARIABLE, SYMBOL, SYMBOL],
    "LT"          => [VARIABLE, SYMBOL, SYMBOL],
    "GT"          => [VARIABLE, SYMBOL, SYMBOL],
    "EQ"          => [VARIABLE, SYMBOL, SYMBOL],
    "AND"         => [VARIABLE, SYMBOL, SYMBOL],
    "OR"          => [VARIABLE, SYMBOL, SYMBOL],
    "NOT"         => [VARIABLE, SYMBOL],
    "INT2CHAR"    => [VARIABLE, SYMBOL],
    "STRI2INT"    => [VARIABLE, SYMBOL, SYMBOL],
    "READ"        => [VARIABLE, TYPE],
    "WRITE"       => [SYMBOL],
    "CONCAT"      => [VARIABLE, SYMBOL, SYMBOL],
    "STRLEN"      => [VARIABLE, SYMBOL],
    "GETCHAR"     => [VARIABLE, SYMBOL, SYMBOL],
    "SETCHAR"     => [VARIABLE, SYMBOL, SYMBOL],
    "TYPE"        => [VARIABLE, SYMBOL],
    "LABEL"       => [LABEL],
    "JUMP"        => [LABEL],
    "JUMPIFEQ"    => [LABEL, SYMBOL, SYMBOL],
    "JUMPIFNEQ"   => [LABEL, SYMBOL, SYMBOL],
    "EXIT"        => [SYMBOL],
    "DPRINT"      => [SYMBOL],
    "BREAK"       => [],

    # bonus instructionsj
    "INT2FLOAT"   => [VARIABLE, SYMBOL],
    "FLOAT2INT"   => [VARIABLE, SYMBOL]
];


// --------------------start of the script -------------------

require_once('input_handler.php');

$input_handler = new InputHandler($argc, $argv);
$input_handler->handle_args();

$lines = $input_handler->load_instructions();

// if there aren't any lines, terminate the program

require_once('generator.php');
if (count($lines) == 0) {
    $generator = new XMLGenerator($lines);
    $generator->generate_header_only($lines);
    exit(0);
}

require_once('analyzer.php');
$analyzer = new Analyzer($lines);
$analyzer->analyze();

# if we got to this part of the code, we can start generating xml

$generator = new XMLGenerator($lines);
$generator->generate_xml();

if ($DEBUG) {echo "SUCCESS!!\n";}

exit();

?>
