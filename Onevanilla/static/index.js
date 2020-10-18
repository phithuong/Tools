// Define card info class
class CardInfoPost {
    constructor(cardNumber, mm, yy, cvv) {
        this.cardnumber = cardNumber;
        this.mm = mm;
        this.yy = yy;
        this.cvv = cvv;
    }

    isSameCardNumber(cardInfo) {
        if (this.cardNumber === cardInfo.cardNumber) {
            return true;
        }
        return false;
    }
}


class CardInfoDetail extends CardInfoPost {
    constructor(no, cardNumber, mm, yy, cvv) {
        super(cardNumber, mm, yy, cvv);
        this.no = no;
        this.balance = "";
        this.status = "";
        this.checkresult = "";
        this.note = "";
    }

    setExtraInfo(balance, status, chekResult) {
        this.balance = balance;
        this.status = status;
        this.checkresult = chekResult;
    }
}


class CardManagement {
    constructor() {
        this.cardInfoDetailCurrentList = new Array();
        this.cardInfoDetailErrorList = new Array();
        this.cardInfoDetailSuccessList = new Array();
    }

    updateExtraInfo(cardList, cardInfo, balance, status, checkResult) {
        let idx = checkCardExist(cardList, cardInfo);
        if (idx !== -1) {
            cardList[idx].setExtraInfo(balance, status, checkResult);
            return 0;
        }
        return -1;
    }
}


// Create table for card information list
const table = $('#cardInfoTable').DataTable({
    columns: [
        { data: 'no' },
        { data: 'cardnumber' },
        { data: 'mm' },
        { data: 'yy' },
        { data: 'cvv' },
        { data: 'balance' },
        { data: 'status' },
        { data: 'checkresult' },
        { data: 'note' }
    ]
});

const cardManagement = new CardManagement();


// Button [Main App] is clicked
$("#main-app").click(function() {
    document.getElementById("collapseExample-1").style.display = "block";
    document.getElementById("collapseExample-2").style.display = "none";
})


// Button [Config] is clicked
$("#config").click(function() {
    document.getElementById("collapseExample-2").style.display = "block";
    document.getElementById("collapseExample-1").style.display = "none";
})


// Button [Start] is clicked.
$("#btn-start").click(function() {
    let infoTextArea = document.getElementById("infoTextArea").value.trim();
    cardManagement.cardInfoDetailCurrentList = new Array();

    let message = "";
    if (infoTextArea == "") {
        message = "You haven't input card info.";
        return;
    }

    infoTextArea = infoTextArea.split("\n");
    let n = infoTextArea.length;
    let numCard = 0;

    let i;
    for (i = 0; i < n; i++) {
        let line = infoTextArea[i].trim();
        if (line == 0) {
            continue;
        }
        numCard += 1;
        let tmp = line.split(",");

        const cardInfoDetail = new CardInfoDetail(i, tmp[0], tmp[1], tmp[2], tmp[3]);

        if (checkCardExist(cardManagement.cardInfoDetailSuccessList, cardInfoDetail) == -1 ||
            checkCardExist(cardManagement.cardInfoDetailErrorList, cardInfoDetail) != -1) {
            cardManagement.cardInfoDetailCurrentList.push(cardInfoDetail);
        }
    }
    // table.rows.add(cardManagement.cardInfoDetailCurrentList).draw();

    // Request to get card information
    let numCurrentCardDetail = cardManagement.cardInfoDetailCurrentList.length;

    async function process() {
        for (i = 0; i < numCurrentCardDetail; i++) {
            const cardInfoPost = new CardInfoPost(
                cardManagement.cardInfoDetailCurrentList[i].cardnumber,
                cardManagement.cardInfoDetailCurrentList[i].mm,
                cardManagement.cardInfoDetailCurrentList[i].yy,
                cardManagement.cardInfoDetailCurrentList[i].cvv);

            let cardInfoResp = await getCardInfo(cardInfoPost).responseJSON;
            console.log(cardInfoResp);

            cardManagement.cardInfoDetailCurrentList[i].setExtraInfo(
                cardInfoResp.balance,
                cardInfoResp.status,
                cardInfoResp.checkresult);

            if (cardInfoResp.balance == "" || cardInfoResp.checkresult !== "OK") {
                cardManagement.cardInfoDetailErrorList.push(cardManagement.cardInfoDetailCurrentList[i]);
            } else {
                cardManagement.cardInfoDetailSuccessList.push(cardManagement.cardInfoDetailCurrentList[i]);
            }

            await drawRowData(cardManagement.cardInfoDetailCurrentList[i]);
            // await table.rows().invalidate().draw();
        }
    }

    process();
});


async function drawRowData(rowData) {
    table.row.add(rowData).draw();
}


function save_config() {
    setting_info = {
        proxy_address: $("#proxy_address").val(),
        proxy_port: $("#proxy_port").val()
    };

    console.log(setting_info);

    $.ajax({
        url: "http://127.0.0.1:5000/save_config",
        type: "POST",
        data: JSON.stringify(setting_info, null, '\t'),
        contentType: 'application/json;charset=UTF-8',
        success: function() {
            console.log("Save config successful.");
        },
        fail: function() {
            console.log("Save config fail.");
        }
    });
}

async function getCardInfo(cardInfoPost) {
    let cardInfoResp;

    return $.ajax({
        type: 'POST',
        url: 'http://127.0.0.1:5000/getCardInfo',
        crossDomain: true,
        async: false,
        data: JSON.stringify(cardInfoPost, null, '\t'),
        contentType: 'application/json;charset=UTF-8',
        success: function(responseData, textStatus, jqXHR) {
            cardInfoResp = responseData;
        },
        error: function(responseData, textStatus, errorThrown) {
            cardInfoResp = responseData;
        }
    });

    // return cardInfoResp;
}

function checkCardExist(cardInfoList, cardInfo) {
    let idx = -1;
    let numCard = cardInfoList.length;

    for (let i = 0; i < numCard; i++) {
        if (cardInfo.isSameCardNumber(cardInfoList[i])) {
            idx = i;
            break;
        }
    }
    return idx;
}