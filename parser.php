<?php

define("VARIABLE", 0);
define("SYMBOL", 1);
define("TYPE", 2);
define("LBL", 3);

// dictionary mappings where key is the name of instruction and value is an array of arguments to that instruction
$instructions_dic = ["MOVE"    => [VARIABLE, SYMBOL],
    "CREATEFRAME" => [],
    "PUSHFRAME"   => [],
    "POPFRAME"    => [],
    "DEFVAR"      => [VARIABLE],
    "CALL"        => [LBL],
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
    "LABEL"       => [LBL],
    "JUMP"        => [LBL],
    "JUMPIFEQ"    => [LBL, SYMBOL, SYMBOL],
    "JUMPIFNEQ"   => [LBL, SYMBOL, SYMBOL],
    "EXIT"        => [SYMBOL],
    "DPRINT"      => [SYMBOL],
    "BREAK"       => [],
];


// --------------------start of the script -------------------

require('input_handler.php');

// Analyzer class checks for lexical and syntactical errors in instructions
class Analyzer {
    private $lines;
    function __construct(array $lines) {
        $this->lines = $lines;
    }

    # function removes comments from the line
    private function remove_comment(string $line): string {
        $comment_split = explode("#", $line);
        $new_line = trim(reset($comment_split));

        return $new_line;
    }

    private function check_variable_syntax(string $arguments) {
         
    }

    private function check_symbol_syntax(string $arguments) {
        
    }

    private function check_type_syntax(string $arguments) {
        
    }
    private function check_label_syntax(string $arguments) {
        
    }

    private function check_syntax(array $instruction_arguments, array $expected_arguments) {
        for ($i = 0; $i < count($expected_arguments); $i++) {
            switch ($expected_arguments[$i]) {
                case VARIABLE:
                    $this->check_variable_syntax($instruction_arguments[$i]);
                    break;

                case SYMBOL:
                    $this->check_symbol_syntax($instruction_arguments[$i]);
                    break;

                case TYPE:
                    $this->check_type_syntax($instruction_arguments[$i]);
                    break;

                case LBL:
                    $this->check_label_syntax($instruction_arguments[$i]);
                    break;
            }
        }
    }

    // return true if 'instruction' has the correct syntax
    private function instruction_ok(string $instruction): bool {
        global $instructions_dic;
        // split by space and trim of whitespace
        $split_instruction = explode(" ", $instruction);
        $split_instruction = array_map('trim', $split_instruction);

        $opcode = $split_instruction[0];                 // name of the instruction
        echo $opcode . "\n";

        // remove the opcode and reset indeces
        $instruction_arguments = array_values(array_slice($split_instruction, 1)); // arguments of the instruction

        // instruction doesn't exist
        if (!array_key_exists($opcode, $instructions_dic)) {
            echo "This instruction doesn't exist\n"; 
            exit(22);
        }

        $expected_arguments = $instructions_dic[$opcode];

        // check if they're of the same length
        if (count($expected_arguments) != count($instruction_arguments)) {
            echo "Incorrect number of arguments\n";
            exit(23);
        }

        /*
        echo "These are the valid arguments for $opcode:"; 
        print_r($expected_arguments);
        echo " and we got";
        print_r($instruction_arguments);
         */

        $this->check_syntax($instruction_arguments, $expected_arguments);
        
        return true;
    }


    public function analyze() {
        echo print_r($this->lines);
        for ($i = 0; $i < count($this->lines); $i++) {
            $this->lines[$i] = $this->remove_comment($this->lines[$i]);
            if (!$this->instruction_ok($this->lines[$i])) {
                exit(22);
            }
        }
    }
}

$input_handler = new InputHandler($argc, $argv);
$input_handler->handle_args();

$lines = $input_handler->load_instructions();

$analyzer = new Analyzer($lines, $instruction_dic);
$analyzer->analyze();
?>