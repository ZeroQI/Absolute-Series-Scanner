$client = new-object System.Net.WebClient
#$client.Credentials =  Get-Credential 
$client.DownloadFile("https://raw.githubusercontent.com/ZeroQI/Absolute-Series-Scanner/master/Scanners/Series/Absolute%20Series%20Scanner.py","Absolute Series Scanner.py")
