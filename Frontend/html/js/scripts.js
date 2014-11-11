/**
* Salto Lockers.
*  JavaScript file for the project.
*/

// Global variables
var in_session = false;

// User identification variables
var id, name, ap, am, discount, mat;


// Login scripts
$('.button').click(function(event){
	ws.send("LOG_IN");
}); 

$(document).ready(function(){
    if ("WebSocket" in window) {
        ws = new WebSocket("ws://localhost:49153");

        ws.onmessage = function (msg) {
        	if (msg == 'INIT_SESSION') {
				alert("OK");

        		in_session = true;

        		ws.send('{"command":"INFO", "params":""}');

	        	$('#main-text').children().remove();

	            $.get('', function(data){			// Load html file for other templates.
	                $('#main-text').html(data);		// Append specific data on the main-text column. 
	            });
	        } else {
	        	alert("User not registered");
	        }
        };

    } else {
        alert("WebSocket not supported");
    }
});