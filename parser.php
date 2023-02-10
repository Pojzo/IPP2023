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
];

    // print help message for parser.php
    function print_help() {
        echo "Usage: php your_program.php [--help] [instructions]" .
        "\n\nOptions:\n  --help    Show this help message\n\n";
    }
    
    // return true if 'instruction' has the correct syntax
    function instruction_ok(string $instruction): bool {
        global $instructions_dic;
        

        // split by space and trim of whitespace
        $split_instruction = explode(" ", $instruction);
        $split_instruction = array_map('trim', $split_instruction);

        $opcode = $split_instruction[0];                 // name of the instruction
        echo $opcode . "\n";
        $instruction_arguments = array_slice($split_instruction, 1); // arguments of the instruction

        // instruction doesn't exist
        if (!array_key_exists($opcode, $instructions_dic)) {
            echo "This instruction doesn't exist\n"; 
            exit(22);
        }

        $valid_arguments = $instructions_dic[$opcode];
        
        // check if they're of the same length
        if (count($valid_arguments) != count($instruction_arguments)) {
            exit(23);
        }

        echo "These are the valid arguments for $opcode:"; 
        print_r($valid_arguments);
        echo " and we got";
        print_r($arguments);
        
        return true;
    }

    // --------------------start of the script -------------------

    $arg_count = $argc - 1; // the first argument is always the file name

    if ($arg_count > 1) {
        // only one or no arguments are valid
        exit(10);
    }

    if ($arg_count == 1) {
        // only --help argument is accepted
        if ($argv[1] != "--help") {
            exit(10);
        }
        print_help();
        exit(0); // terminate the program with exit code 0 after printing help
    }

    $instructions = "";

    // read all instructions from stdin
    while ($line = fgets(STDIN)) {
        $instructions .= $line;
    }
    
    // split the input program into lines and
    $lines = explode("\n", $instructions);

    // check if header is present
    if ($lines[0] != ".IPPcode23") {
        exit(21);
    }

    // remove the header since it won't be needed anymore
    $lines = array_slice($lines, 1);

    // clear any whitespace from front and back
    $clear_lines = array_map('trim', $lines);

    // remove comments
    $clear_lines = array_filter($clear_lines, function($line) {
        return substr($line, 0, 1) != '#';
    });

    foreach ($clear_lines as $line) {
        # remove comments from any part of the line
        $comment_split = explode("#", $line);
        $comment_free_line = trim(reset($comment_split));
        if (!instruction_ok($comment_free_line)) {
            exit(22);
        }
    }
?>
