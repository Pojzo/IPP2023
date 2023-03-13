<?php
// Analyzer class checks for lexical and syntactical errors in instructions
class Analyzer {
    private $lines;
    private $data_types = array("int", "bool", "string", "nil");
    private $scopes = array("GF", "TF", "LF");
    public function __construct(array $lines) {
        $this->lines = $lines;
    }

    // return true if $const is of type string based on rules specified in the
    private function is_string_(string $const): bool {
        return preg_match("/^(\\\\[0-9][0-9][0-9]|[^#\s\\\\])*\s*$/u", $const);
    }

    // return true if $const is of type int
    private function is_int_(string $const): bool {
        return is_numeric($const);
    }

    // return true if $const is of type bool
    private function is_bool_(string $const): bool {
        return $const == "true" or $const == "false";
    }

    // return true if $const is of type type
    private function is_type(string $const): bool {
        return in_array($const, $this->data_types);
    }

    // return true if $identifier is correct
    private function is_identifier(string $identifier): bool {
        return preg_match('/^[a-zA-Z$&%\*!\?_-][\w$&%\*!\?]*$/', $identifier) === 1;
    }

    // check if variable has correct syntax based on its datatype
    private function check_variable_syntax(string $variable) {
        global $DEBUG;
        $pattern = '/^(GF|LF|TF)@.+/';
        if (!preg_match($pattern, $variable)) {
            if ($DEBUG) {echo "Invalid symbol format";}
            exit(23);
        }

        $split_variable = explode("@", $variable);
        $scope = trim($split_variable[0]);
        $identifier = trim($split_variable[1]);

        // incorrect scope
        if (!in_array($scope, $this->scopes)) {
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
        $pattern = '/^(string|int|bool|nil|GF|LF|TF)@.+/';
        if (!preg_match($pattern, $symbol)) {
            // check for exception string@
            if ($symbol == "string@") {return True;}
            if ($DEBUG) {echo "Invalid symbol format";}
            exit(23);
        }

        // string@hello
        $split_symbol = explode("@", $symbol);
        $type = trim($split_symbol[0]); // type of variable, left side of @
        $name = trim($split_symbol[1]); // name of variable, right side of @

        // check if we're dealing with constant
        if (in_array($type, $this->data_types)) {
            if ($type == "string") {
                if (!$this->is_string_($name)) {
                    if ($DEBUG) {echo "Symbol isn't of type string\n";}
                    exit(23);
                }
            }

            elseif ($type == "int") {
                if (!$this->is_int_($name)) {
                    if ($DEBUG) {echo "Symbol isn't of type int\n";}
                    exit(23);
                }
            }

            elseif ($type == "bool") {
                if (!$this->is_bool_($name)) {
                    if ($DEBUG) {echo "Symbol isn't of type bool\n";}
                    exit(23);
                }
            }
            elseif ($type == "nil") {
                if (!$this->is_type($name)) {
                    if ($DEBUG) {echo "Symbol isn't of type nil\n";}
                    exit(23);
                }
            }
        }
        // check if we're dealing with variable
        elseif (in_array($type, $this->scopes)) {
            if (!$this->is_identifier($name)) {
                if ($DEBUG) {echo "Incorrect identifier in symbol $type/$name\n";}
                exit(23);
            }
        }
        else {
            if ($DEBUG) {echo "Incorrect datatype $type/$name\n";}
            exit(23);
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

    private function check_label_syntax(string $label) {
        global $DEBUG;
        if (!$this->is_identifier($label)) {
            if ($DEBUG) {echo "Failed in check label syntax\n";}
            exit(23);
        }
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

            case LABEL:
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
                exit(23);
            }
        }
    }

    // return true if 'instruction' has the correct syntax
    private function instruction_ok(string $instruction) {
        global $instructions_dic;
        global $DEBUG;
        // split by any number of spaces and
        $split_instruction = preg_split('/\s+/', $instruction);
        $split_instruction = array_map('trim', $split_instruction);

        $opcode = $split_instruction[0];                 // name of the instruction
        # echo $opcode . "\n";

        // remove the opcode and reset indeces
        $instruction_arguments = array_values(array_slice($split_instruction, 1)); // arguments of the instruction

        // instruction doesn't exist
        if (!array_key_exists(strtoupper($opcode), $instructions_dic)) {
            if ($DEBUG) {echo "Instruction doesn't exist\n";}
            # echo "This instruction doesn't exist\n";
            exit(22);
        }

        $expected_arguments = $instructions_dic[strtoupper($opcode)];

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
?>
