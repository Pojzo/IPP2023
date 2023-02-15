<?php

$DEBUG = False;

// InputHandler class loads instructions and returns them for further processing
class InputHandler {
    private $arg_count;
    private $argv;

    function __construct(int $argc, array $argv) {
        $this->arg_count = $argc - 1; // the first argument is always the file name
        $this->argv = $argv;
    }

    // print help message for parser.php
    private function print_help() {
        echo "Usage: php your_program.php [--help] [instructions]" .
            "\n\nOptions:\n  --help    Show this help message\n\n";
    }

    public function handle_args() {
        if ($this->arg_count > 1) {
            // only one or no arguments are valid
            exit(10);
        }

        if ($this->arg_count == 1) {
            // only --help argument is accepted
            if ($this->argv[1] != "--help") {
                exit(10);
            }
            $this->print_help();
            exit(0); // terminate the program with exit code 0 after printing help
        }
    }

    private function remove_comment(string $line): string {
        $comment_split = explode("#", $line);
        $new_line = trim(reset($comment_split));

        return $new_line;
    }

    private function handle_header(array $lines): array {
        global $DEBUG;
        // check if header is present
        // there could be comment after header
        
        if (str_contains($lines[0], '#')) {
            if (trim(explode("#", $lines[0])[0]) != ".IPPcode23") {
                if ($DEBUG) {echo "50 riadok input_handler \n";}
                exit(21);
            }
        }
        else {
            if (strtolower((trim($lines[0]) != ".IPPcode23"))) {
                if ($DEBUG) {echo "56 riadok input_handler \n";}
                exit(21);

            }
        }

        // remove the header
        $lines = array_slice($lines, 1);
        return $lines;
    }

    public function load_instructions(): array {
        $instructions = "";

        // read all instructions from stdin
        while ($line = fgets(STDIN)) {
            $instructions .= $line;
        }

        // split the input program into lines
        $lines = explode("\n", $instructions);

        // comments can be before header
        while (substr(trim($lines[0]), 0, 1) == '#' or empty(trim($lines[0]))) {
            $lines = array_slice($lines, 1);
        }

        // check header
        $lines = $this->handle_header($lines);

        // clear any whitespace from front and back
        $clear_lines = array_map('trim', $lines);

        for ($i = 0; $i < count($clear_lines); $i++) {
            $clear_lines[$i] = $this->remove_comment($clear_lines[$i]);
        }

        /*
        // remove lines that start with a comment
        $clear_lines = array_filter($clear_lines, function($line) {
            return substr($line, 0, 1) != '#';
        });
         */

        // return non-empty lines and reset their indeces
        return array_values(array_filter($clear_lines, function($line) {
            return !empty($line);
        }));
    }
}
?>
