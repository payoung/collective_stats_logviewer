jQuery(document).ready(function() {
    $(document).on('ready', function(){
        $('dl.url-details dd').hide();
    });
    $(document).on('click', 'dt.url-help', function(){
        $('dl.url-details dd').toggle();
        plot();
    });
});

function plot(){
	var options = {
		lines: {
			show: true,
		},
		points: {
			show: true,
            fillColor: "#0062E3",
		},
        xaxis: { mode: "time",
                 timeformat: "%M:%S",
                 minTickSize: [1, "second"]
        },
        yaxis: {
            ticks: [0,0.5,1,2,3,4,6,10],
        },
        legend: {
            show: true
        }
	};

    var data = [];
    function onDataReceived(series) {
        $.each(series.data, function(key, value){
            time = parseFloat(value.render_time);
            timestamp = (new Date(value.timestamp)).getTime();
            data.push([timestamp, time]);
        });

		$.plot($("#placeholder1"), [
        {
            label: "Render Time",
            data: data,
            color: "#0062E3",
        }
    ], options);
	};

	$.ajax({
		url: '/reponse_time_details?url=/newscenter/inthenewsview',
		type: "GET",
		dataType: "json",
		success: onDataReceived
	});
}
