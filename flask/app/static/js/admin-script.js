const inputsDayDown = document.getElementsByClassName('inputsDayDown')[0]
const editBtnModal = document.getElementsByClassName('editBtnDayDown')[0];
const cancelBtnModal = document.getElementsByClassName('cancelBtnDayDown')[0]
const saveBtnModal = document.getElementsByClassName('saveBtnDayDown')[0]
const dayDownTextArea = document.getElementsByClassName('inputDayDownReason')[0];

editBtnModal.addEventListener('click', dayDownToEdit);
cancelBtnModal.addEventListener('click', dayDownToRead);
saveBtnModal.addEventListener('click', saveReasonDayDown);

function dayDownToEdit(e) {
    dayDownTextArea.value =dayDownReason.innerText;
    displaysDayDown.style.display = 'none';
    inputsDayDown.style.display = 'flex';
}

function dayDownToRead(e){
    displaysDayDown.style.display = 'flex';
    inputsDayDown.style.display = 'none';
}

function saveReasonDayDown(e) {
    const [year, month, day] = dayDownHeader.innerText.split(' ');
    let newReason = dayDownTextArea.value;
    if (!newReason) {
        console.log('here');
        newReason = 'Geen reden bekend...';
    }

    fetch(`/daydown/${year}/${month}/${day}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'reason': newReason})
        }).then(res => res.json())
        .then(jsonRes => {
            dayDownReason.innerText = jsonRes.reason
            dayDownToRead()
        })
        .catch(console.log)
}