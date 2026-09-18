let reps = 0;
let phase = "up";
const TARGET_REPS = 10;
let DOWN_THRESHOLD = 100, UP_THRESHOLD = 160;

function checkRep(angle) {
    if (angle > UP_THRESHOLD && phase === "down") {
        phase = "up";
        reps++;
        document.getElementById("rep-display").textContent = reps + " / " + TARGET_REPS;

        if (TARGET_REPS <= reps) {
            unlock();
        }

    }
    if (angle < DOWN_THRESHOLD && phase === "up"){
        phase = "down"
       
    }
}

// hip, knee, ankle
function calculateAngle(a,b,c) {
    // b is the vertex - the joint you're measuring the bend at (KNEE)
    const angleRad = Math.atan2(c.y - b.y, c.x - b.x) -
    Math.atan2(a.y - b.y, a.x - b.x);

    let angleDeg = Math.abs(angleRad * 180 / Math.PI);

    if (angleDeg > 180) {
        angleDeg = 360 - angleDeg;
    }
    
    return angleDeg

}

function unlock() {
 window.parent.postMessage({ workForItUnlocked: true }, "*");
}