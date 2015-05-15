

$( document ).ready(function() {
    $.getJSON('/city-list', function(result) {

    	$('#typeahead_departure_city').typeahead({
	    	source: {
	    		data: result.cities
	    	}	    
		});

    	$('#typeahead_city1').typeahead({
	    	source: {
	    		data: result.cities
	    	}	    
		});

    	$('#typeahead_city2').typeahead({
	    	source: {
	    		data: result.cities
	    	}	    
		});


    });
    
});