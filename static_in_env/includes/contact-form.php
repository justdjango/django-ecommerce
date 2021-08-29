<?php

$string = file_get_contents("config.json");
$option = json_decode($string);

define("MAIL_HOST", $option->MAIL_HOST);
define("MAIL_TITLE", $option->MAIL_TITLE);

if( isset($_POST['name']) && isset($_POST['email']) && isset($_POST['msg'])){
    $name = $_POST['name'];
    $email = $_POST['email'];
    $msg = nl2br($_POST['msg']);
    if (MAIL_HOST != null) {
        $to = MAIL_HOST;
    } else {
        $to = "lebach.tk@gmail.com";
    }
    $from = $email;
    if (MAIL_TITLE != null) {
        $subject = MAIL_TITLE;
    } else {
        $subject = '[Consulting] Contact Form Message';
    }
    $message = '<b>Name:</b> '.$name.' <br><b>Email:</b> '.$email.' <br> <p>'.$msg.'</p>';
    $headers = "From: $from\n";
    $headers .= "MIME-Version: 1.0\n";
    $headers .= "Content-type: text/html; charset=iso-8859-1\n";
    if( mail($to, $subject, $message, $headers) ) {
        $serialized_data = '{"type":"success", "message":"Contact form successfully submitted. Thank you, I will get back to you soon!"}';
        echo $serialized_data;
    } else {
        $serialized_data = '{"type":"danger", "message":"Contact form failed. Please send again later!"}';
        echo $serialized_data;
    }
};
