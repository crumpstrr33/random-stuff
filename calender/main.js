var MONTHS = ["January", "February", "March", "April",
                  "May", "June", "July", "August",
                  "September", "October", "November", "December"]
var DAY_COUNT = [31, 28, 31, 30, 31 ,30, 31, 31, 30, 31, 30, 31]
var MONTH_LENS = {}
var MONTH_SUMS = {}
var tot = 0;
for (i = 0; i < 12; i++) {
    MONTH_SUMS[MONTHS[i]] = tot;
    MONTH_LENS[MONTHS[i]] = DAY_COUNT[i];
    tot += DAY_COUNT[i];
};

var date = new Date();
CUR_DAY = date.getDate();
CUR_MONTH = MONTHS[date.getMonth()]
CUR_YEAR = date.getFullYear()
makeMonth(CUR_MONTH, CUR_YEAR);

function getPrevMonthYear(m, y) {
    var prevMonth = (m == "January" ? "December" : MONTHS[MONTHS.indexOf(m) - 1]);
    return [prevMonth, (m == "January" ? y - 1 : y)];
};

function getNextMonthYear(m, y) {
    var nextMonth = (m == "December" ? "January" : MONTHS[MONTHS.indexOf(m) + 1]);
    return [nextMonth, (m == "December" ? Number(y) + 1 : y)];
};

// Builds the calender
function makeMonth(month, year) {
    var days = document.getElementById("days");

    // Remove the old month
    while (days.hasChildNodes()) {
        days.removeChild(days.lastChild);
    };

    // Check number of leap years since, a year isn't a leap year if it is
    // divisible by 100 but not by 400. Starting at 1600 since Gregorian calender
    // was introduced in 1582 and I'm rounding up to 1600
    var y = year - 1600;
    var numLeapYears = (Math.ceil(y / 4) - Math.ceil(y / 100) + Math.ceil(y / 400)) % 7;

    // Earliest year chosen as 1600, that starts on a Tuesday
    var start = ((year - 1600) % 7 + MONTH_SUMS[month] % 7 + numLeapYears - 1) % 7;
    if (start == -1) {
        start = 6;
    };
    var numDays = MONTH_LENS[month]

    // Check if leap day and February
    if (month === "February" && year % 4 == 0) {
        if (!(year % 100 == 0 && year % 400 != 0)) {
            numDays++;
        };
    };
    (year % 100 == 0) & !(year % 400)

    // 42 boxes (6 rows)
    for (i = 1; i < 43; i++) {
        var day = document.createElement("div");
        var dayNum = i - start

        if (i < start + 1) {
            // Month before
            var [curMonth, curYear] = getPrevMonthYear(month, year);
            dayNum = MONTH_LENS[curMonth] - start + i;
            day.innerHTML = "<div class=num>" + dayNum + "</div>"
            day.className = "day box faded";
        } else if (i > numDays + start) {
            // Month after
            var [curMonth, curYear] = getNextMonthYear(month, year);
            dayNum = i - start - numDays;
            day.innerHTML = "<div class=num>" + dayNum + "</div>"
            day.className = "day box faded";
        } else {
            // Current month
            var [curMonth, curYear] = [month, year];
            day.innerHTML = "<div class=num>" + dayNum + "</div>";
            day.className = "day box curMonth"
        }
        day.id = "D" + curYear + curMonth + dayNum;
        days.appendChild(day);
    };

    // Special styling for current day
    curDay = days.querySelector("#D" + CUR_YEAR + CUR_MONTH + CUR_DAY);
    if (curDay != null) {
        var curDayBorder = document.createElement("div");
        curDayBorder.className = "curDay";
        if (CUR_MONTH != month) {
            curDayBorder.style.opacity = 0.5;
        }

        curDay.appendChild(curDayBorder);
    }

    document.getElementById("month").innerHTML = month + " " + year;

    checkToGreyButton();
};

/* Buttons */
function getMonthYear() {
    return document.getElementById("month").innerHTML.split(" "); 
}

// Button for Previous Month
document.getElementById("prevMonth").onclick = function() {
    var [month, year] = getMonthYear();
    var [newMonth, newYear] = getPrevMonthYear(month, year);
    makeMonth(newMonth, newYear);
};
// Button for Previous Year
document.getElementById("prevYear").onclick = function() {
    var [month, year] = getMonthYear();
    makeMonth(month, Number(year) - 1);
};
// Button for Next Month
document.getElementById("nextMonth").onclick = function() {
    var [month, year] = getMonthYear();
    var [newMonth, newYear] = getNextMonthYear(month, year);
    makeMonth(newMonth, newYear);
};
// Button for Next Year
document.getElementById("nextYear").onclick = function() {
    var [month, year] = getMonthYear();
    makeMonth(month, Number(year) + 1);
};

// Grey out previous buttons at year 1600
function checkToGreyButton() {
    var [month, year] = getMonthYear();
    var prevMonth = document.getElementById("prevMonth");
    var prevYear = document.getElementById("prevYear");

    prevMonth.disabled = (month === "January" && year == 1600 ? true : false);
    prevYear.disabled = (year == 1600 ? true : false);
}