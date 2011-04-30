<?php
	header("Cache-Control: no-cache, must-revalidate");
	header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");

	if (@$_GET['id']) {
		echo json_encode(uploadprogress_get_info($_REQUEST['id']));
		exit();
	}

	if (@$_POST['UPLOAD_IDENTIFIER'])
		exit();
	
	$uuid = uniqid();
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<title>Jquery WITS Form</title>
	    <link rel="stylesheet" type="text/css" href="http://t.wits.sg/misc/css/reset.css"/>
	    <link rel="stylesheet" type="text/css" href="http://t.wits.sg/misc/css/base.css"/>
	    <link rel="stylesheet" type="text/css" href="http://t.wits.sg/misc/css/template.css"/>
	    <link rel="stylesheet" type="text/css" href="http://t.wits.sg/misc/css/form.css"/>
		<script type="text/javascript">
			var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
			document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
			</script>
			<script type="text/javascript">
			try {
			var pageTracker = _gat._getTracker("UA-1120774-3");
			pageTracker._trackPageview();
			} catch(err) {}
		</script>
		<script type="text/javascript" src="http://t.wits.sg/misc/js/jQuery/jquery.js"></script>
		<script type="text/javascript" src="js/jquery.progressbar.min.js"></script>
		<script type="text/javascript">
			var progress_key = '<?= $uuid ?>';

			$(document).ready(function() {
				$("#pb1").progressBar();
				$("#pb2").progressBar({ barImage: 'images/progressbg_yellow.gif'} );
				$("#pb3").progressBar({ barImage: 'images/progressbg_orange.gif', showText: false} );
				$("#pb4").progressBar(65, { showText: false, barImage: 'images/progressbg_red.gif'} );
				$(".pb5").progressBar({ max: 2000, textFormat: 'fraction', callback: function(data) { if (data.running_value == data.value) { alert("Callback example: Target reached!"); } }} );
				$("#uploadprogressbar").progressBar();
			});

			function beginUpload() {
				$("#uploadprogressbar").fadeIn();

				var i = setInterval(function() { 
					$.getJSON("demo.php?id=" + progress_key, function(data) {
						if (data == null) {
							clearInterval(i);
							location.reload(true);
							return;
						}

						var percentage = Math.floor(100 * parseInt(data.bytes_uploaded) / parseInt(data.bytes_total));
						$("#uploadprogressbar").progressBar(percentage);
					});
				}, 1500);

				return true;
			}
		</script>
		<style type="text/css">
			table tr { vertical-align: top; }
			table td { padding: 3px; }
			div.contentblock { padding-bottom: 25px; }	
			#uploadprogressbar { display: none; }
		</style>
	</head>
	<body>
		<div id="container">
			<div style="float: right; text-align: right; width: 300px;">download me at <a href="http://t.wits.sg">http://t.wits.sg</a></div>
			<div class="contentblock">
				<h2>Progress Bars &amp; Controls</h2>
				<table>
					<tr><td>Default Multicolored Bar</td><td><span class="progressBar" id="pb1">75%</span></td></tr>
					<tr><td>Yellow Bar</td><td><span class="progressBar" id="pb2">35%</span></td></tr>
					<tr><td>Orange Bar (No Text)</td><td><span class="progressBar" id="pb3">55%</span></td></tr>
					<tr><td>Red Bar (No Text)</td><td><span class="progressBar" id="pb4">85%</span></td></tr>
					<tr><td>Default Multicolored Bar with max value of 2000</td><td><span class="progressBar pb5">32</span></td></tr>
				</table>
				<strong>Some controls: </strong>
				<a href="#" onclick="$('#pb1').progressBar(20);">20</a> |
				<a href="#" onclick="$('#pb1').progressBar(40);">40</a> |
				<a href="#" onclick="$('#pb1').progressBar(60);">60</a> |
				<a href="#" onclick="$('#pb1').progressBar(80);">80</a> |
				<a href="#" onclick="$('#pb1').progressBar(100);">100</a>
			</div>

			<div class="contentblock">
				<h2>Usage: </h2>
<pre class="ln-"><code class="js">
$(document).ready(function() {
	$("#pb1").progressBar();
	$("#pb2").progressBar({ barImage: 'images/progressbg_yellow.gif'} );
	$("#pb3").progressBar({ barImage: 'images/progressbg_orange.gif', showText: false} );
	$("#pb4").progressBar(65, { showText: false, barImage: 'images/progressbg_red.gif'} );
	$(".pb5").progressBar({ max: 2000, textFormat: 'fraction', callback: function(data) { if (data.running_value == data.value) { alert("Callback example: Target reached!"); } }} );
	$("#uploadprogressbar").progressBar();
});
</code></pre>
			
			</div>
			<div class="contentblock">
				<h2>Progress Bars Form Example</h2>
				<a href="demo.txt">Download the PHP Source here</a>
				<div class="edit_panel">
					<form action="demo.php" target="progressFrame" method="post" id="uploadform" enctype="multipart/form-data" onsubmit="beginUpload();">
						<input type="hidden" name="UPLOAD_IDENTIFIER" id="progress_key" value="<?= $uuid ?>" />
						<table class="form">
							<tr><td class="labelcol"><label for="firstname">First Name</label><em>*</em></td><td class="inpulcol"><input type="text" name="firstname" id="firstname" class="text" /></td></tr>
							<tr><td class="labelcol"><label for="lastname">First Name</label><em>*</em></td><td class="inpulcol"><input type="text" name="lastname" id="lastname" class="text" /></td></tr>
							<tr><td class="labelcol"><label for="password">First Name</label><em>*</em></td><td class="inpulcol"><input type="password" name="password" id="password" class="text" /></td></tr>
							<tr><td class="labelcol"><label for="ulfile1">File 1</label></td>
							    <td><input type="file" name="ulfile1" id="ulfile1" /></td>
							</tr>
							<tr><td class="labelcol"><label for="ulfile2">File 2</label></td>
							    <td><input type="file" name="ulfile2" id="ulfile2" /></td>
							</tr>
							<tr><td class="labelcol"><label for="ulfile3">File 3</label></td>
							    <td><input type="file" name="ulfile3" id="ulfile3" /></td>
							</tr>
							<tr><td class="labelcol"></td>
								<td class="inputcol"><input type="submit" value="Submit" />
								<br />
								<span class="progressbar" id="uploadprogressbar">0%</span>	
							</td></tr>
						</table>
					</form>
				</div>
			</div>
			
			<div class="contentblock">
				<h2>Upload Form Javascript: </h2>
<pre class="ln-"><code class="js">
var progress_key = '<?= $uuid ?>';

// this sets up the progress bar
$(document).ready(function() {
	$("#uploadprogressbar").progressBar();
});

// fades in the progress bar and starts polling the upload progress after 1.5seconds
function beginUpload() {
	// uses ajax to poll the uploadprogress.php page with the id
	// deserializes the json string, and computes the percentage (integer)
	// update the jQuery progress bar
	// sets a timer for the next poll in 750ms
	$("#uploadprogressbar").fadeIn();

	var i = setInterval(function() { 
		$.getJSON("demo.php?id=" + progress_key, function(data) {
			if (data == null) {
				clearInterval(i);
				location.reload(true);
				return;
			}

			var percentage = Math.floor(100 * parseInt(data.bytes_uploaded) / parseInt(data.bytes_total));
			$("#uploadprogressbar").progressBar(percentage);
		});
	}, 1500);
}
</code></pre>
			</div>
		</div>
		<!-- Ok, you so need this iframe for Safari and Chrome to work, the webkit engine doesnt allow ajax calls to be made after a form begins submission -->
		<iframe style="display: none;" name="progressFrame"></iframe>
	</body>
</html>
