var c1 = {};
var c2 = {};
var cities = [c1, c2];
var previousCity;
var winningCity;
var HIGHLIGHT = "color: #42B872";

$(document).ready(function () {
    // hide results table and preference sliders
    $('#results-table').hide();
    $('#final-decision-form').hide();
    $("#algo-result").hide();
    $("#component-weights").hide();
    $(".loader").hide();

    $("#preference-form").on("submit", getCityData);
    $("#pp-choice").on("click", exploreCity);
    $(".importance-slider").on("change", reCalculateDestination);

});

function determineDestination() {

    var costWeight = parseInt($("#cost-weight").val(), 10);
    var foodWeight = parseInt($("#food-weight").val(), 10);
    var weatherWeight = parseInt($("#weather-weight").val(), 10);
    var totalWeight = costWeight + foodWeight + weatherWeight;

    weatherDelta = calcWeatherDelta(c1, c2);
    flightDelta = calcFlightDelta(c1, c2);
    colDelta = calcColDelta(c1, c2);
    starDelta = calcstarDelta(c1, c2);

    var wowDelta = (c1.wow - c2.wow) / c1.wow;
    if (wowDelta > 0) { $("#wow-1").attr("style", HIGHLIGHT);}
    else if (wowDelta < 0) {$("#wow-2").attr("style", HIGHLIGHT);}

    var dataDelta = (foodWeight/totalWeight)*starDelta -
                    (costWeight*0.5/totalWeight)*colDelta -
                    (costWeight*0.5/totalWeight)*flightDelta -
                    (weatherWeight/totalWeight)*weatherDelta;

    winningCity = compareDeltas(dataDelta, wowDelta);

    showWinner(winningCity);

}

function calcWeatherDelta(c1, c2) {
    var idealTemp = $("input:radio[name=ideal-temp]:checked").val();
    var weatherDeltaCity1 = Math.abs(c1.weather - idealTemp);
    var weatherDeltaCity2 = Math.abs(c2.weather - idealTemp);
    var weatherDelta = (weatherDeltaCity1 - weatherDeltaCity2) / weatherDeltaCity1;
    if (weatherDelta > 0) { $("#weather-2").attr("style", HIGHLIGHT);}
    else if (weatherDelta < 0) {$("#weather-1").attr("style", HIGHLIGHT);}

    return weatherDelta;

}

function calcColDelta(c1, c2) {
    var colDelta = (c1.costOfLiving - c2.costOfLiving) / (c1.costOfLiving);
    if (colDelta > 0) { $("#col-2").attr("style", HIGHLIGHT); }
    else if (colDelta < 0) { $("#col-1").attr("style", HIGHLIGHT); }

    return colDelta;
}

function calcFlightDelta(c1, c2) {
    var flightDelta = (c1.airfare - c2.airfare) / (c1.airfare);
    if (flightDelta > 0) { $("#flight-2").attr("style", HIGHLIGHT); }
    else if (flightDelta < 0) { $("#flight-1").attr("style", HIGHLIGHT); }

    return flightDelta;
}

function calcstarDelta(c1, c2) {
    var starDelta;

    if (c1.stars > 0) {
        starDelta = (c1.stars - c2.stars) / c1.stars;
    } else if (c2.stars > 0) {
        starDelta = -1;   // city 2 is 100% better
    } else {
        starDelta = 0;
    }

    if (starDelta > 0) { $("#food-1").attr("style", HIGHLIGHT);}
    else if (starDelta < 0) {$("#food-2").attr("style", HIGHLIGHT);}

    return starDelta;

}

function compareDeltas(dataDelta, wowDelta) {
     if (dataDelta + wowDelta > 0) {
        winningCity = c1;
    }

    else if (dataDelta + wowDelta < 0) {
        winningCity = c2;
    }

   else {
        winningCity = Math.random() > 0.5 ? c1 : c2;
    }

    return winningCity;

}

function showWinner(winningCity) {
    $("#pp-choice").html('Explore ' + winningCity.city);
    $("#pp-choice-text").html("Pensive Passport's algorithm has selected " +
                                "<span class='primary-color'>" +
                                "<strong>" + winningCity.city + "</strong></span>!");

    $("#pp-choice").data("cityId", winningCity.cityId);
    $("#algo-result").show();

}

function prepDom() {
    $("#gather-data-button").hide();
    $("#city-specific-pref").hide();
    $("#travel-dates").hide();
    $("#departure-dropdown").hide();
    $("#temp-selectors").hide();
    $('#results-table').show();
    $('#final-decision-form').show();
    $('#component-weights').show();
    $(".photo-carousel").hide();
    $("#general-pref").hide();
    $(".city-header").hide();
    $("#travel-pref-header").hide();
    $(".loader").fadeIn("slow");

}

function getCityData(evt) {
    evt.preventDefault();
    prepDom();

    var apiResponses = 0;

    for (i=1; i < cities.length + 1; i++) {
        loopCities(i);
    }

    function loopCities(i) {
        var cityInfo = cities[i-1];

        $("#wow-"+i).html($("#wow-input-"+i).val());
        cityInfo.wow = $("#wow-input-"+i).val();

        var url = '/get-city-data?airport='+ $("#airport-"+i).val();
        $.get(url, function (result) {
            cityInfo.city = result.city;
            cityInfo.cityId = result.cityId;
            cityInfo.country = result.country;
            cityInfo.stars = getNum(parseInt(result.stars, 10));
            cityInfo.costOfLiving = parseInt(result.costOfLiving, 10);
            $('#food-'+i).html(cityInfo.stars + ' ' +
                                "<img class='michelin-star' src='/static/images/michelinstar.png'>");
            $('#col-'+i).html(cityInfo.costOfLiving);
            apiResponses++;
            if (apiResponses===6) {    // all calls have completed
                apiCallsCompleted();}

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
                if (apiResponses===6) {    // all calls have completed
                    apiCallsCompleted();}
            }
        );

        $.post("/get-weather",
            {depart_date: $("#depart-date").val(),
            destination: $("#airport-"+i).val()},
            function (result) {
                $('#weather-'+i).html(result.low + " - " + result.high + " F");
                cityInfo.weather = (parseInt(result.low, 10) + parseInt(result.high, 10))/2;
                apiResponses ++;
                if (apiResponses===6) {    // all calls have completed
                    apiCallsCompleted();}
            }
        );
    }

}

function reCalculateDestination() {
    previousCity = winningCity.city;

    determineDestination();

    if (previousCity === winningCity.city) {
        $("#pp-choice-text").html("After recalculation, Pensive Passport " +
                                    "<strong>still</strong> chooses " + winningCity.city + "!");
    }

    else {$("#pp-choice-text").html("After recalculation, Pensive Passport now selects " +
                                    "<span class='primary-color'><strong>" + winningCity.city + "</strong></span>!");
    }
    }

function exploreCity(evt) {
    $(".loader").fadeIn("slow");
    var cityId = $(this).data("cityId");

    window.location = "/winning-city?city_id=" + cityId;

}

function getNum(val)
    {
       if (isNaN(val))
         return 0;
       else
         return val;
    }

function storeTrips() {
    $.post('/store-trips',
    {'trip1':JSON.stringify(c1),
    'trip2':JSON.stringify(c2)},
    function(result) {});
}

function apiCallsCompleted() {
    storeTrips();
    determineDestination();
    $(".loader").hide();
}
