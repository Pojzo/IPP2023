<?php
use PHPUnit\Framework\TestCase;

require 'input_handler.php';

class input_handler_tests extends TestCase
{
    private function remove_comment(string $line): string {
        $comment_split = explode("#", $line);
        $new_line = trim(reset($comment_split));

        return $new_line;
    }

    public function testRemovesCommentFromLineWithHashtag()
    {
        $line = 'This line has a comment # This is a comment';
        $expected = 'This line has a comment';

        $this->assertEquals($expected, $this->remove_comment($line));
    }

    public function testRemovesCommentFromLineWithHashtagAndLeadingWhitespace()
    {
        $line = '   This line has a comment # This is a comment';
        $expected = 'This line has a comment';

        $this->assertEquals($expected, $this->remove_comment($line));
    }

    public function testRemovesCommentFromLineWithHashtagAndTrailingWhitespace()
    {
        $line = 'This line has a comment # This is a comment  ';
        $expected = 'This line has a comment';

        $this->assertEquals($expected, $this->remove_comment($line));
    }

    public function testReturnsLineUnchangedWhenNoHashtagPresent()
    {
        $line = 'This line has no comment';
        $expected = 'This line has no comment';

        $this->assertEquals($expected, $this->remove_comment($line));
    }
}
