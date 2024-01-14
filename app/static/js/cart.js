
function createRoomHtml(room) {
    return `
        <div class="border row my-3 mx-2 p-3 bg-white cardItem">
            <img class="col-5" style="width: 350px" src="https://digital.ihg.com/is/image/ihg/intercontinental-ho-chi-minh-city-6392782644-4x3?wid=540&amp;fit=constrain" alt="Card image">
            <div class="col-7 container-fluid cardBody">
                <h2 class="card-title">${room.room_type_name}</h2>
                <p class="card-text">${room.room_price.toFixed(0)} VNĐ</p>
                <p class="card-text">Còn ${room.room_available} phòng trống !!!</p>
                <a href="" class="btn btn-primary mx-1">Xem chi tiết</a>
                <a href="/checkOutBooking/${room.room_type_id}" class="btn btn-primary mx-1">Book Now!</a>
            </div>
        </div>
    `;
}

// find room
const findRoom = document.getElementById('searchRoom');
const resultContainer = document.getElementById('resultContainer');
if(findRoom){
    findRoom.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission
    const selectedDate = document.getElementById('date').value;

// Thêm giờ cố định (12:00 PM)
    const defaultTime = '14:00';
    const fullDate = `${selectedDate} ${defaultTime}`;

    const formData = {
        date: fullDate,
        numGuests: document.getElementById('num_guests').value,
        numNights: document.getElementById('num_nights').value,
    };
    fetch('/api/room', {
        method: "post",
        body: JSON.stringify({
            "date": formData.date,
            "guests": formData.numGuests,
            "nights": formData.numNights
        }),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        localStorage.setItem('nameCus', JSON.stringify(formData));
        resultContainer.innerHTML = '';

        // Tạo và thêm phần tử HTML cho mỗi phòng vào container
        data.forEach(room => {
            const roomHtml = createRoomHtml(room);
                    console.log(room)
            resultContainer.innerHTML += roomHtml;
        });
    })
});
}

// seachRoomAdmin

function createRoomAdminHtml(room, availableRoom) {
    const isRoomBook = availableRoom.some(available => available.room_name === room.name);
    const isCheckInStatus =  availableRoom.some(available => available.checkIn_status === false);  // Giả sử có biến bookingStatus để kiểm tra trạng thái đặt phòng.
    const selectedDate = document.getElementById('dateAdmin').value;
    const numberOfDaysValue = document.getElementById('num_nightsAdmin').value;
    let style = '';
    if (isRoomBook) {
        if(isCheckInStatus){
            style = 'background-color: yellow';
        }
            style = 'background-color: red';
    } else {
        style = 'background-color: white';
    }
    let url = ``;
    let bookingNameCusHtml = '';
    url = `/admin/booking/${room.id}/?date=${selectedDate}&numNights=${numberOfDaysValue}`
    for (const available of availableRoom) {
        if (available.room_name === room.name) {
            bookingNameCusHtml = `<div style="font-size: 16px">${available.user_name}</div>`;
            url = `/admin/booking/${room.id}/?user=${available.user_id}&booking_id=${available.booking_id}`;
            break;
        }
    }

    return `
        <div class="col-2 m-3">
            <a class="btn btn border border-2 rounded" style="${style}" href="${url}">
                <div style="width: 150px; height: 100px">
                    <div style="font-size: 16px">${room.room_type}</div>
                    <h3 class="m-0">${room.name}</h3>
                    ${bookingNameCusHtml}
                </div>
            </a>
        </div>
    `;
}

const findRoomAdmin = document.getElementById('searchRoomAdmin');
const resultContainerAdmin = document.getElementById('resultContainerAdmin');
if(findRoomAdmin){
    findRoomAdmin.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission
    const selectedDate = document.getElementById('dateAdmin').value;
    const defaultTime = '14:00';
    const fullDate = `${selectedDate} ${defaultTime}`;
    const formData = {
        date: fullDate,
        numNights: document.getElementById('num_nightsAdmin').value,
    };
    fetch('/api/roomAdmin', {
        method: "post",
        body: JSON.stringify({
            "date": formData.date,
            "nights": formData.numNights
        }),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        console.log(data)

        resultContainerAdmin.innerHTML = '';

        // Tạo và thêm phần tử HTML cho mỗi phòng vào container
        data.room_list.forEach(room => {
            const roomHtml = createRoomAdminHtml(room, data.availableRoom);
            resultContainerAdmin.innerHTML += roomHtml;
        });
    })
});
}

// booking infoooo
const gettingInfo = document.getElementById("");
if(gettingInfo){
    gettingInfo.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = {
        nameCus:document.getElementById('nameCustomer').value,
        phoneNumber:document.getElementById('numPhoneCus').value,
        emailCus:document.getElementById('emailCustomer').value
    };
    console.log(formData)
});
}

// submitBooking

function submitBooking(id, roomId, name, phone, email, checkIn, checkOut) {
    const defaultCheckInTime = '14:00';
    const defaultCheckOutTime = '12:00';
    const checkInDay = `${checkIn} ${defaultCheckInTime}`;
    const checkOutDay = `${checkOut} ${defaultCheckOutTime}`;
    fetch(`/api/submitBooking/${id}`, {
        method: "post",
        body: JSON.stringify({
            booking_id: id,
            roomType_id: roomId,
            nameCustomer: name,
            phoneNumber: phone,
            emailCustomer: email,
            checkInDay: checkInDay,
            checkOutDay: checkOutDay
        }),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        window.location.href = `/reviewBooking/endBooking/${JSON.stringify(data)}`
    })
}


function checkInRoom(room_id, booking_id,user_id, checkInDate, numNights, roomPrice ){
    fetch(`/api/checkInRoom/${room_id}`, {
        method: "post",
        body: JSON.stringify({
            room_id: room_id,
            booking_id: booking_id,
            user_id:user_id,
            checkIn_date: checkInDate,
            numNights: numNights,
        }),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        console.log(data)
        window.location.reload()
    })
}
// Check Out Room
function checkOutRoom(id){
    fetch(`/api/checkOutRoom/${id}`, {
        method: "post",
        body: JSON.stringify({
            room_id: id,
        }),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        console.log(data)
        window.location.reload()
    })
}



const bookingRoomAdmin = document.getElementById('bookingRoomAdmin');

if (bookingRoomAdmin) {
    bookingRoomAdmin.addEventListener('submit', (event) => {
        event.preventDefault();
        const nameCus = document.getElementById('nameCus').value;
        const room_id = document.getElementById('room_id').value;
        const numNights = document.getElementById('numDays').value;
        const phoneNum = document.getElementById('phoneNum').value;
        const selectedDate = document.getElementById('dayAdmin').value;
        console.log(nameCus)
        const defaultTime = '14:00';
        const fullDate = `${selectedDate} ${defaultTime}`;

        fetch('/api/bookingRoomAdmin', {
            method: "post",
            body: JSON.stringify({
                "checkIn": fullDate,
                "numNights": numNights,
                "room_id": room_id,
                "nameCus": nameCus,
                "phoneNum": phoneNum,
            }),
            headers: {
                'Content-Type': "application/json"
            }
        }).then(function (res) {
            return res.json();
        }).then(function (data) {
            alert("đặt phòng thành công")
            window.location.href = `/admin/booking/`
        });
    });
}
// function updateCart(id, obj) {
//     obj.disabled = true;
//     fetch(`/api/cart/${id}`, {
//         method: 'put',
//         body: JSON.stringify({
//             'quantity': obj.value
//         }),  headers: {
//             'Content-Type': "application/json"
//         }
//     }).then(res => res.json()).then(data => {
//         obj.disabled = false;
//         let c = document.getElementsByClassName('cart-counter');
//         for (let d of c)
//             d.innerText = data.total_quantity
//     });
// }
//
// function deleteCart(id, obj) {
//     if (confirm("Ban chac chan xoa khong?") === true) {
//         obj.disabled = true;
//         fetch(`/api/cart/${id}`, {
//             method: 'delete'
//         }).then(res => res.json()).then(data => {
//             obj.disabled = false;
//             let c = document.getElementsByClassName('cart-counter');
//             for (let d of c)
//                 d.innerText = data.total_quantity
//
//             let r = document.getElementById(`product${id}`);
//             r.style.display = "none";
//         });
//     }
// }