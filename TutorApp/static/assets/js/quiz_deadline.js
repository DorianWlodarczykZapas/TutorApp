document.addEventListener("DOMContentLoaded", function() {
        const rawDeadLine = document.getElementById("quiz-deadline").textContent;
        const deadlineString = JSON.parse(rawDeadLine);
        const deadline = new Date(deadlineString);
        const timerElement = document.getElementById("quiz-timer");

        function updateTimer() {
            const now = new Date();
            const millisecondsLeft = deadline - now;

            if(millisecondsLeft <=0){
                timerElement.textContent = "Time is up!";
                clearInterval(intervalId);
                document.querySelector("form").submit();
                return;
            }

            const totalSeconds = Math.floor(millisecondsLeft / 1000);
            const hours = Math.floor(totalSeconds / 3600)
            const secondsRemainingAfterHours = totalSeconds - (hours * 3600)
            const minutes = Math.floor(secondsRemainingAfterHours / 60);
            const seconds = secondsRemainingAfterHours % 60;
            if(hours > 0){
            timerElement.textContent =
            `${hours.toString().padStart(2,"0")}:${minutes.toString().padStart(2,"0")}:${seconds.toString().padStart(2,"0")}`;
            }
            else {

            timerElement.textContent =
            `${minutes.toString().padStart(2,"0")}:${seconds.toString().padStart(2,"0")}`;
            }
        }


        const intervalId = setInterval(updateTimer,1000);
        updateTimer();
        });