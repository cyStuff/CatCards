window.onload = () => {
	console.log("Script Loaded");
	var pass1 = document.getElementById("password");
	var pass2 = document.getElementById("passcheck");

	var check1 = document.getElementById("checkmark1");
	var check2 = document.getElementById("checkmark2");
	var short = document.getElementById("short");
	var x = document.getElementById("X");

	var submit = document.getElementById("submit");

	function onkey(event) {
		if (pass1.value == pass2.value && pass1.value.length >= 8) {
			check2.hidden = false;
			x.hidden = true;
			check1.hidden = false;
			short.hidden = true;
			submit.disabled = false;
			return;
		}
		submit.disabled = true;
		if (pass1.value == pass2.value) {
			check2.hidden = false;
			x.hidden = true;
		}
		else {
			check2.hidden = true;
			x.hidden = false;
		}
		if (pass1.value.length >= 8) {
			check1.hidden = false;
			short.hidden = true;
		}
		else {
			check1.hidden = true;
			short.hidden = false;
		}
	}

	pass1.addEventListener("keyup", onkey);
	pass2.addEventListener("keyup", onkey);
};