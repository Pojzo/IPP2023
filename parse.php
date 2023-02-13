<?php

define("VARIABLE", 0);
define("SYMBOL", 1);
define("TYPE", 2);
define("LABEL", 3);

$DEBUG = False;


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
];


// --------------------start of the script -------------------

require_once('input_handler.php');

// Analyzer class checks for lexical and syntactical errors in instructions
class Analyzer {
    private $lines;
    private $data_types = array("int", "bool", "string", "nil");
    public function __construct(array $lines) {
        $this->lines = $lines;
    }

    // return true if $const is of type string based on rules specified in the
    private function is_string(string $const): bool {
        return True;
        // TODO 
    }
    
    // return true if $const is of type int 
    private function is_int(string $const): bool {
        return is_int($string);
    }

    // return true if $const is of type bool
    private function is_bool(string $const): bool {
        return $const == "true" or $const == "false";
    }

    // return true if $const is of type type
    private function is_type(string $const): bool {
        return in_array($const, $this->data_type);
    }

    // return true if $identifier is correct
    private function is_identifier(string $identifier): bool {
        return preg_match('/^[a-zA-Z$&%\*!\?_-][\w$&%\*!\?]*$/', $identifier) === 1;
    }
    
    // check if variable has correct syntax based on its datatype
    private function check_variable_syntax(string $variable) {
        global $DEBUG;
        $split_variable = explode("@", $variable);
        // missing @ in variable
        if (count($split_variable) == 1) {
            if ($DEBUG) {echo "$split_variable == 1\n";}
            exit(23);
        }
        
        if (count($split_variable) > 2) {
            if ($DEBUG) {echo "$split_variable > 2\n";}
            exit(23);
        }

        $scope = $split_variable[0];
        $identifier = $split_variable[1];
        
        // incorrect scope
        if (!in_array($scope, array("LF", "TF", "GF"))) {
            if ($DEBUG) {echo "Incorrect scope\n";}
            exit(23);
        }

        // incorrect identifier
        if (!$this->is_identifier($identifier)) {
            if ($DEBUG) {echo "Incorrect identifier\n";}
            exit(23);
        }
    }

    // check if symbol has correct syntax - <datatype>@const
    private function check_symbol_syntax(string $symbol) {
        global $DEBUG;
        $split_symbol = explode("@", $symbol);
        // missing @ in $symbol
        if (count($split_symbol) == 1) {
            if ($DEBUG) {echo "$split_symbol == 1\n";}
            exit(23);
        }

        if (count($split_symbol) > 2) {
            if ($DEBUG) {echo "$split_symbol > 2\n";}
            exit(23);
        }

        // string@hello
        $type = $split_symbol[0]; // type of variable, left side of @
        $name = $split_symbol[1]; // name of variable, right side of @

        // check if datataype is correct
        var_dump($type);
        if (!in_array($type, $this->data_types)) {
            if ($DEBUG) {echo "Incorrect datatype\n";}
            echo "tu som2\n";
            exit(23);
        }

        if ($type == "string") {
            if (!$this->is_string()) {
                if ($DEBUG) {echo "Symbol isn't of type string\n";}
                exit(23);
            }
        }

        elseif ($type == "int") {
            if (!$this->is_int()) {
                if ($DEBUG) {echo "Symbol isn't of type int\n";}
                exit(23);
            }
        }

        elseif ($type == "bool") {
            if (!$this->is_bool()) {
                if ($DEBUG) {echo "Symbol isn't of type bool\n";}
                exit(23);
            }
        }
        elseif ($type == "nil") {
            if (!$this->is_type()) {
                if ($DEBUG) {echo "Symbol isn't of type nil\n";}
                exit(23);
            }
        }

    }

    // check if $type is correct type xd
    private function check_type_syntax(string $type) {
        global $DEBUG;
        if (!in_array($type, $this->data_types)) {
            if ($DEBUG) {echo "Failed in check type syntax\n";}
            exit(23);
        }
    }

    // TODO
    private function check_label_syntax(string $label) {
        
    }

    private function check_syntax(array $instruction_arguments, array $expected_arguments) {
        for ($i = 0; $i < count($expected_arguments); $i++) {
            switch ($expected_arguments[$i]) {
            case VARIABLE:
                $this->check_variable_syntax($instruction_arguments[$i]);
                break;

            case SYMBOL:
                return;
                $this->check_symbol_syntax($instruction_arguments[$i]);
                break;

            case TYPE:
                return;
                $this->check_type_syntax($instruction_arguments[$i]);
                break;

            case LABEL:
                return;
                $this->check_label_syntax($instruction_arguments[$i]);
                break;
            }
        }
    }

    public function analyze() {
        # echo print_r($this->lines);
        for ($i = 0; $i < count($this->lines); $i++) {
            # echo $this->lines[$i];
            // $this->lines[$i] = $this->remove_comment($this->lines[$i]);
            if (!($this->instruction_ok($this->lines[$i]))) {
                if ($DEBUG) {echo "Instruction is not ok\n";}
                exit(22);
            }
        }
    }

    // return true if 'instruction' has the correct syntax
    private function instruction_ok(string $instruction) {
        global $instructions_dic;
        // split by space and trim of whitespace
        $split_instruction = explode(" ", $instruction);
        $split_instruction = array_map('trim', $split_instruction);

        $opcode = $split_instruction[0];                 // name of the instruction
        # echo $opcode . "\n";

        // remove the opcode and reset indeces
        $instruction_arguments = array_values(array_slice($split_instruction, 1)); // arguments of the instruction

        // instruction doesn't exist
        if (!array_key_exists($opcode, $instructions_dic)) {
            if ($DEBUG) {echo "Instruction doesn't exist\n";}
            # echo "This instruction doesn't exist\n"; 
            exit(22);
        }

        $expected_arguments = $instructions_dic[$opcode];

        // check if they're of the same length
        if (count($expected_arguments) != count($instruction_arguments)) {
            if ($DEBUG) {echo "Invalid number of arguments\n";}
            # echo "Incorrect number of arguments\n";
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
}

class MyXMLWriter {
    public static function write(SimpleXMLElement $xml) {

        $dom = new DOMDocument("1.0");
        $dom->preserveWhiteSpace = false;
        $dom->formatOutput = true;
        $dom->loadXML($xml->asXML());

        $formattedXML = $dom->saveXML();

        echo $formattedXML;
        exit;
        
        global $DEBUG;
        // Save the XML to a file
        $file = fopen('generated.xml', 'w');
        if (!$file) {
            if ($DEBUG) {echo "Error opening output file\n";}
            // error opening output file
            exit(12);
        }

        if (!fwrite($file, $formattedXML)) {
            // I guess the same error as the previous one
            exit(12);
        }
        fclose($file);
    }
}

class XMLGenerator {
    private $header;
    private $lines;
    private $num_instructions;
    private $arg_functions;

    public function __construct(array $lines) {
        $this->header = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?' .'>'.'<program></program>');
        $this->header->addAttribute('language', 'IPPcode23');
        $this->lines = $lines;
        $this->num_instructions = 0;
        $this->arg_functions = [VARIABLE => [$this, 'generate_variable_arg_xml'],
            SYMBOL   => [$this, 'generate_symbol_arg_xml'  ],
            TYPE     => [$this, 'generate_type_arg_xml'    ],
            LABEL    => [$this, 'generate_label_arg_xml'   ]
        ];
    }

    // generate xml for argument of type variable
    private function generate_variable_arg_xml(SimpleXMLElement $arg_xml, string $arg_string) {
        $arg_xml->addAttribute('type', 'var');
        $arg_xml[0] = $arg_string;
    }    

    // generate xml for argument of type symbol
    private function generate_symbol_arg_xml(SimpleXMLElement $arg_xml, string $arg_string) {
        [$data_type, $name] = explode("@", $arg_string);
        $arg_xml->addAttribute('type', $data_type);
        $arg_xml[0] = $name;
    }

    // generate xml for argument of type 'type'
    private function generate_type_arg_xml(SimpleXMLElement $arg_xml, string $arg_string) {
        $arg_xml->addAttribute('type', 'type');
        $arg_xml[0] = $arg_string;
    }

    // generate xml for argument of type label
    private function generate_label_arg_xml(SimpleXMLElement $arg_xml, string $arg_string) {
        $arg_xml->addAttribute('type', 'label');
        $arg_xml[0] = $arg_string;
    }

    // return arg element in xml format
    private function generate_arg_xml(SimpleXMLElement $parent_instruction, int $arg_count, int $type, string $arg_string) {
        $arg_xml = $parent_instruction->addChild("arg" . strval($arg_count));
        // $arg_functions stores functions for corresponding argument types
        $this->arg_functions[$type]($arg_xml, $arg_string);
    }

    // return instruction element in xml format
    private function generate_instruction_xml(string $opcode, array $arguments): SimpleXMLElement {
        global $instructions_dic;
        $instruction_xml = $this->header->addChild("instruction");

        $instruction_xml->addAttribute('order', strval($this->num_instructions));
        $instruction_xml->addAttribute('opcode', strtoupper($opcode));

        $argument_types = $instructions_dic[$opcode];

        // instruction without any arguments
        if (count($argument_types) == 0) {
            $instruction_xml[0] = ' ';
            $instruction_xml[0] = '';
        }


        // this won't happen if there aren't any arguments
        for ($arg_count = 0; $arg_count < count($argument_types); $arg_count++) {
            $this->generate_arg_xml($instruction_xml, $arg_count + 1, $argument_types[$arg_count], $arguments[$arg_count]);
        }

        return $instruction_xml;
    }

    // generate the output xml
    public function generate_xml() {
        for ($i = 0; $i < count($this->lines); $i++) {
            $arguments = explode(" ", $this->lines[$i]);
            $opcode = array_shift($arguments); // shift the array so that it doesn't contain opcode
            $this->num_instructions += 1;      // increase the instruction count

            $this->generate_instruction_xml($opcode, $arguments); // create new instruction
            // $this->header->addChild($instruction_xml); // add it to the header as child

        }
        // echo $this->header->asXML();
        MyXMLWriter::write($this->header);
    }
}

$input_handler = new InputHandler($argc, $argv);
$input_handler->handle_args();

$lines = $input_handler->load_instructions();


$analyzer = new Analyzer($lines);
$analyzer->analyze();
#
# if we got to this part of the code, we can start generating xml

$generator = new XMLGenerator($lines);
$generator->generate_xml();

if ($DEBUG) {echo "SUCCESS!!\n";}

exit();

?>
