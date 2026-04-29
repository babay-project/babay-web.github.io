<?php
// Izinkan akses dari domain Anda saja
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

// URL API Asli
$apiUrl = "http://ezweystock.petrix.id/gpt/payment";

// Ambil data yang dikirim dari form JS
$data = file_get_contents("php://input");

// Kirim request ke API menggunakan cURL (lebih stabil)
$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json'
]);

$response = curl_exec($ch);
curl_close($ch);

// Kirim balik respon dari API ke browser Anda
echo $response;
?>
