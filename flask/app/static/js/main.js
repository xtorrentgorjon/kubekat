setNumOfColumns() // kick it off ordered

const displaysDayDown = document.getElementsByClassName('displayDayDown')[0]
const dayDownReason = document.getElementsByClassName('dayDownReason')[0]
const dayDownHeader = document.getElementsByClassName('modalHeader')[0]
const modalExitBtn = document.getElementsByClassName('modalExitBtn')[0]
const modal = document.getElementsByClassName('modalWrapper')[0]

const daysOff = document.getElementsByClassName('day_below_SLA')

const monthsInt = {
  Jan: 1,
  Feb: 2,
  Mrt: 3,
  Apr: 4,
  Mei: 5,
  Jun: 6,
  Jul: 7,
  Aug: 8,
  Sep: 9,
  Okt: 10,
  Nov: 11,
  Dec: 12
}

////////////////////////// Add event listenenrs
for (let dayOff of daysOff) {
  dayOff.addEventListener('click', clickDayOff)
}
window.addEventListener('resize', setNumOfColumns)
modal.addEventListener('click', hideModal)
modalExitBtn.addEventListener('click', hideModal)

// Sets the numbers of columns accourding to the width of the screen (for the calendar)
function setNumOfColumns() {
  const doc = document.getElementsByClassName('year_frame')[0]
  const NUM_COLUMNS = Math.floor(window.innerWidth / 300)
  let templateColumns = ''
  for (let i = 0; i < NUM_COLUMNS; i++) {
    templateColumns += '300px '
  }
  doc.style.gridTemplateColumns = templateColumns
}

// Reacts to clicking on a dat off, gets the date value from the box (and parent) and calls show modal
function clickDayOff(e) {
  if (e.target.className == 'day_below_SLA') {
    return
  }

  const day = e.target.innerText.trim()
  const month = e.target.parentElement.parentElement.parentElement.parentElement.firstElementChild.innerText
    .substring(0, 3)
    .trim()
  const yearText = document
    .getElementsByClassName('month_selection_string')[0]
    .firstElementChild.innerText.split(' ')
  const year = yearText[yearText.length - 1].trim()
  showModal(day, month, year)
}

// Sends request to api to get when it was off. then accourding to that it shows a bar indicating the time at which it was down and the status code
function showModal(day, month, year) {
  monthNum = monthsInt[month]
  fetch(`/daydown/${year}/${month}/${day}`)
    .then(res => res.json())
    .then(json => {
      dayDownReason.innerText = json.reason
      dayDownHeader.innerText = `${year} ${month} ${day}`
      wrapper = document.getElementsByClassName('modalWrapper')[0]
      wrapper.style.display = 'block'
      getDurationDown(year, monthNum, day)
        .then(duration => {
          displayDownOnStatusBar(duration)
        })
        .catch(console.log)
    })
    .catch(console.log)
}

// Sends the request to the api and parses json and returns it
function getDurationDown(year, month, day) {
  return fetch(`/daydown/duration/${year}/${month}/${day}`)
    .then(res => res.json())
    .catch(console.log)
}

const toBeRemovedAtCloseElements = [] // elements created at the status bar by js will be stored here to be destroyed later when the modal is closed

// closes the model, removing all the created nodes from the array above,
function hideModal(e) {
  if (
    e.target.className !== 'modalExitBtn' &&
    e.target.className !== 'modalWrapper'
  ) {
    return
  }

  // remove the elements created at the status bar
  toBeRemovedAtCloseElements.forEach(item => item.remove())
  toBeRemovedAtCloseElements.length = 0

  modal.style.display = 'none'

  // If I'm the admin then make sure it is turned to read at the end
  if (typeof dayDownToRead === 'function') {
    dayDownToRead()
  }
}

// creates a status bar with all the down times on it (creates all necessary nodes)
function displayDownOnStatusBar(duration) {
  // get width dedicated to each millisecond
  const statusBar = document.getElementsByClassName('statusBar')[0]
  const width = statusBar.offsetWidth
  const millisecondsADay = 1000 * 60 * 60 * 24
  const widthPerMillisecond = width / millisecondsADay

  // key is the starting of the duration
  for (let startDuration in duration) {
    durationObj = duration[startDuration]

    const startOfDown = new Date(startDuration)
    const endOfDown = new Date(durationObj['end'])

    const durationMilliseconds = endOfDown - startOfDown

    const timeBeginDay = new Date(
      startOfDown.getFullYear(),
      startOfDown.getMonth(),
      startOfDown.getDate(),
      0,
      0,
      0
    )
    const offsetFromStartDay = startOfDown - timeBeginDay

    // create a node and append it
    const statusBarPart = document.createElement('span')
    statusBarPart.style.left = widthPerMillisecond * offsetFromStartDay
    statusBarPart.style.width = widthPerMillisecond * durationMilliseconds
    statusBarPart.classList.add('downStatus')
    statusBarPart.innerHTML = `<span class="showIfAdmin">${
      durationObj.httpCode
    }</span>`
    statusBar.append(statusBarPart)

    // create label start down
    const beginDownHour = document.createElement('span')
    beginDownHour.innerText = `${
      startOfDown.getHours() == '0' ? '00' : startOfDown.getHours()
    }:${startOfDown.getMinutes() == '0' ? '00' : startOfDown.getMinutes()}`
    beginDownHour.style.left = `${widthPerMillisecond * offsetFromStartDay -
      20}px`
    beginDownHour.classList.add('beginDownHour')
    statusBar.append(beginDownHour)

    // create label end down
    const endDownHour = document.createElement('span')
    endDownHour.innerText = `${
      endOfDown.getHours() == '0' ? '00' : endOfDown.getHours()
    }:${endOfDown.getMinutes() == '0' ? '00' : endOfDown.getMinutes()}`
    endDownHour.style.left = `${widthPerMillisecond * offsetFromStartDay +
      widthPerMillisecond * durationMilliseconds -
      10}px`
    endDownHour.classList.add('endDownHour')
    statusBar.append(endDownHour)

    toBeRemovedAtCloseElements.push(statusBarPart, beginDownHour, endDownHour)
  }
}
