var c1 = {};
var c2 = {};
var cities = [c1, c2];
var previousCity;
var winningCity;

$(document).ready(function () {
    // hide results table and preference sliders
    $('#results-table').hide();
    $('#final-decision-form').hide();
    $("#algo-result").hide();
    $("#component-weights").hide();
    $(".loader").hide()

    $("#preference-form").on("submit", getCityData);
    $("#pp-choice").on("click", exploreCity);
    $(".importance-slider").on("change", reCalculateDestination);

});

function prepDom() {
    $("#gather-data-button").hide();
    $("#city-specific-pref").hide();
    $("#travel-dates").hide();
    $("#departure-dropdown").hide();
    $("#temp-selectors").hide();
    $('#results-table').show();
    $('#final-decision-form').show();
    $('#component-weights').show()
    $(".photo-carousel").hide();
    $("#general-pref").hide();
    $(".city-header").hide();

}

function determineDestination(cities) {
    var c1 = cities[0];  // try "city1" or even "c1" FIXME
    var c2 = cities[1];
    var HIGHLIGHT = "color:#66CDAA";

    var idealTemp = $("input:radio[name=ideal-temp]:checked").val();

    var costWeight = parseInt($("#cost-weight").val());
    var foodWeight = parseInt($("#food-weight").val());
    var weatherWeight = parseInt($("#weather-weight").val());
    var totalWeight = costWeight + foodWeight + weatherWeight;

    var flightDelta = (c1.airfare - c2.airfare) / (c1.airfare);
    if (flightDelta > 0) { $("#flight-2").attr("style", HIGHLIGHT) }
    else if (flightDelta < 0) { $("#flight-1").attr("style", HIGHLIGHT) }

    var colDelta = (c1.costOfLiving - c2.costOfLiving) / (c1.costOfLiving);
    if (colDelta > 0) { $("#col-2").attr("style", HIGHLIGHT)}
    else if (colDelta < 0) {$("#col-1").attr("style", HIGHLIGHT)}

    var weatherDeltaCity1 = c1.weather - idealTemp;
    var weatherDeltaCity2 = c2.weather - idealTemp;
    var weatherDelta = (weatherDeltaCity1 - weatherDeltaCity2) / weatherDeltaCity1;
    if (weatherDelta > 0) { $("#weather-2").attr("style", HIGHLIGHT)}
    else if (weatherDelta < 0) {$("#weather-1").attr("style", HIGHLIGHT)}

    var wowDelta = (c1.wow - c2.wow) / c1.wow;
    if (wowDelta > 0) { $("#wow-1").attr("style", HIGHLIGHT)}
    else if (wowDelta < 0) {$("#wow-2").attr("style", HIGHLIGHT)}

    var starDelta;

    // determine relative delta in number of stars in city
    if (c1.food > 0) {
        starDelta = (c1.food - c2.food) / c1.food;
    } else if (c2.food > 0) {
        starDelta = -1;   // city 2 is 100% better
    } else {
        starDelta = 0;    
    }

    if (starDelta > 0) { $("#food-1").attr("style", HIGHLIGHT)}
    else if (starDelta < 0) {$("#food-2").attr("style", HIGHLIGHT)}

    var dataDelta = (foodWeight/totalWeight)*starDelta -
                    (costWeight*0.5/totalWeight)*colDelta -
                    (costWeight*0.5/totalWeight)*flightDelta - 
                    (weatherWeight/totalWeight)*weatherDelta
    
    if (dataDelta + wowDelta > 0) {
        winningCity = c1;
    }

    else if (dataDelta + wowDelta < 0) {
        winningCity = c2;
    }

   else { 
        // winningCity = Math.random() > 0.5 ? c1 : c2;
        var trips = [c1, c2];
        winningCity = trips[Math.floor(Math.random()*trips.length)];
    }

    $("#pp-choice").html('Explore ' + winningCity.city);
    $("#pp-choice-text").html("Pensive Passport's algorithm has selected: " + 
                                "<span style='color:red;'>" + 
                                "<strong>" + winningCity.city + "</strong></span>");

    $("#pp-choice").data("cityId", winningCity.cityId);
    $("#algo-result").show();

}          

function getCityData(evt) {   
    evt.preventDefault();
    prepDom();
    
    var apiResponses = 0;

    for (i=1; i < cities.length + 1; i++) { 
        loopCities(i) 
    }
    
    function loopCities(i) {
        var cityInfo = cities[i-1];

        // wow_input = $("#wow-input-" + i);

        $("#wow-"+i).html($("#wow-input-"+i).val());
        cityInfo.wow = $("#wow-input-"+i).val()

        var url = '/get-city-data?airport='+ $("#airport-"+i).val();
        $.get(url, function (result) {                
            cityInfo.city = result.city;
            cityInfo.cityId = result.cityId;
            cityInfo.country = result.country;
            cityInfo.food = parseInt(result.food);
            cityInfo.food = getNum(cityInfo.food);
            cityInfo.costOfLiving = parseInt(result.costOfLiving);
            $('#food-'+i).html(cityInfo.food + ' ' + 
                                "<img class='michelin-star' src='/static/images/michelinstar.jpg'>");
            $('#col-'+i).html(cityInfo.costOfLiving);
            
            }
        );
                    
        $.post("/get-flight",
            {depart_date: $("#depart-date").val(), 
            return_date: $("#return-date").val(), 
            origin: $("#departure-airport").val(), 
            destination: $("#airport-"+i).val()},
            function (result) {
                $('#flight-'+i).html("$" + result.airfare);
                cityInfo.airfare = result.airfare;
                apiResponses++;
                if (apiResponses===4) {    // all calls have completed
                    // FIXME: this is the same, make a function
                    $.post('/store-trips',
                        {'trip1':JSON.stringify(cities[0]), 
                        'trip2':JSON.stringify(cities[1])}, 
                        // FIXME don't need a function body, 99.999% sure
                        function(result) {});
                    determineDestination(cities)};
            }
        );

        $.post("/get-weather",
            {depart_date: $("#depart-date").val(), 
            destination: $("#airport-"+i).val()},
            function (result) {
                $('#weather-'+i).html(result.low + " - " + result.high + " F");
                cityInfo.weather = (parseInt(result.low) + parseInt(result.high))/2;
                apiResponses ++;
                if (apiResponses===4) {    // all calls have completed
                    $.post('/store-trips',
                        {'trip1':JSON.stringify(cities[0]),
                        'trip2':JSON.stringify(cities[1])},
                        function(result) {});
                    determineDestination(cities)};
            }
        );
    }

}

function reCalculateDestination() {
    previousCity = winningCity.city;
    
    determineDestination(cities);
    if (previousCity === winningCity.city) {
        $("#pp-choice-text").html("After recalculation, Pensive Passport " + 
                                    "<strong>still</strong> chooses " + winningCity.city + "!");
    }

    else {$("#pp-choice-text").html("After recalculation, Pensive Passport now selects " + 
                                    "<span style='color:red'>" + winningCity.city + "</span>!");
    } 
    }        

function exploreCity(evt) {
    $(".loader").fadeIn("slow");
    var cityId = $(this).data("cityId");

    window.location = "/results?city_id=" + cityId;

}

function getNum(val)
    {
       if (isNaN(val)) 
         return 0;
       else
         return val;
    }

function storeTrips(cities) {
    $.post('/store-trips',
    {'trip1':JSON.stringify(cities[0]),
    'trip2':JSON.stringify(cities[1])},
    function(result) {});
}
