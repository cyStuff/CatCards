window.onload = () => {
	var time = document.getElementById('pack_time').innerHTML;
	const arr = time.split(':');
	var diff = (arr[0]*60*60) + (arr[1]*60) + parseInt(arr[2])
	console.log("time remaining: " + diff);
	//var diff = 3;
	var startTime = new Date().getTime();
	setInterval(() => {
		diff -= 1;
		var timer = document.getElementById('time');
		if (diff < 0) {
			diff += 300;
			var count = document.getElementById('packs')
			console.log(count.innerHTML);
			count.innerHTML = parseInt(count.innerHTML) + 1
		}
		if (timer) {
			var hours = Math.floor(diff / (60 * 60))
			var minutes = Math.floor((diff / 60) % 60);
			var seconds = Math.floor(diff % 60);
			timer.innerHTML = hours.toString().padStart(2, '0')+':'+minutes.toString().padStart(2, '0')+':'+seconds.toString().padStart(2, '0');
		}
	}, 1000); // out of sync with server to have better user experience.
};