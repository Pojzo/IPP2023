<?php

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

    // generate only header and print it
    public function generate_header_only() {
        MyXMLWriter::write($this->header);
    }

    // generate xml for argument of type variable
    private function generate_variable_arg_xml(SimpleXMLElement $arg_xml, string $arg_string) {
        $arg_xml->addAttribute('type', 'var');
        $arg_xml[0] = $arg_string;
    }    

    // generate xml for argument of type symbol
    private function generate_symbol_arg_xml(SimpleXMLElement $arg_xml, string $arg_string) {
        [$data_type, $name] = explode("@", $arg_string);
        if ($data_type == "GF" or $data_type == "LF" or $data_type == "TF") {
            $arg_xml->addAttribute('type', 'var');
            $arg_xml[0] = $arg_string;
        }
        else {
            $arg_xml->addAttribute('type', $data_type);
            $arg_xml[0] = $name;
        }
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

        $argument_types = $instructions_dic[strtoupper($opcode)];

        // instruction without any arguments
        if (count($argument_types) == 0) {
        }

        # while there is "" in arguments, remove it 
        while (($key = array_search("", $arguments)) !== false) {
            unset($arguments[$key]);
        }
        # reset the array
        $arguments = array_values($arguments);

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

?>
