document.addEventListener("DOMContentLoaded", () => {
    const totalQuestions = JSON.parse(
        document.getElementById("total-questions-data").textContent
    );
    const secondsPerQuestion = JSON.parse(
        document.getElementById("seconds-per-question-data").textContent
    );

    const questionCountSelect = document.getElementById("id_question_count");
    const timeEstimateDisplay = document.getElementById("time-estimate");

    function formatDuration(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        const parts = [];
        if (hours > 0) parts.push(`${hours} h`);
        if (minutes > 0) parts.push(`${minutes} min`);
        if (seconds > 0 || parts.length === 0) parts.push(`${seconds} s`);

        return parts.join(" ");
    }

    function updateTimeEstimate() {
        const selectedValue = questionCountSelect.value;
        const questionCount = selectedValue === "all"
            ? totalQuestions
            : parseInt(selectedValue, 10);

        const totalSeconds = questionCount * secondsPerQuestion;
        timeEstimateDisplay.textContent = formatDuration(totalSeconds);
    }

    questionCountSelect.addEventListener("change", updateTimeEstimate);

    updateTimeEstimate();
});