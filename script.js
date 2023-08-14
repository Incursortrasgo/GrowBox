window.onload = function() {
  const temp = document.querySelector("#temp");
  const humidity = document.querySelector("#humidity");
  const errorCard = document.querySelector("#error-card")

  const myRequest = new Request("/api/sensordata");

  fetch(myRequest)
    .then((response) => {
      if (!response.ok) {
        errorCard.classList.remove("is-hidden")
      } else {
        return response.json();
      }
    })
    .then((response) => {
      errorCard.classList.add("is-hidden");
      temp.innerHTML = response.temp;
      humidity.innerHTML = response.humidity;
    });
  };
