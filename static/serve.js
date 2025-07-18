const button1 = document.getElementById('button-team1');
const TOTAL_COST = 1200;
let remainingMoney = TOTAL_COST;
const createButton = document.getElementById('Register');
// Button1 check only passes on index page
if (button1){
    button1.addEventListener('click', function() {
        const container = document.getElementById('new');
        const htmlToInsert = `
                <div class="leaderboard-container" id="side-bar" style="width: 20%; left: 70%; top: 79.5%; height: 120%; justify-content: center;">
                <button class="link-button" id="x-button" style="color: #ff0000">&times</button>
                <h2>Gang Bangers of All Time</h2>
                <div class="team-view">
                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 1</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 2</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 3</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 4</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 5</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 6</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 7</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 8</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 9</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 10</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 11</div>
                        <div class="status">Empty</div>
                    </div>

                    <div class="player-card" style="margin: 3%">
                        <div class="label">Player 12</div>
                        <div class="status">Empty</div>
                    </div>
                </div>
                </div>
        `;
        container.insertAdjacentHTML('beforeend', htmlToInsert);
        });
    
    document.addEventListener("click", function(event) {
        if (event.target.matches("#x-button")) {
        const sideBar = document.getElementById('side-bar');
        sideBar.remove();
    }
    });
}


document.addEventListener('DOMContentLoaded', () => {

    const playerButtons = document.querySelectorAll('.cost-card'); // Refers to player buttons on the right
    const teamSlots = document.querySelectorAll('.team-player'); // Refers to team slots on the left
    let budget = document.querySelector('.budget-box .amount'); // Load initial budget amount when content loads
    const searchInput = document.getElementById('player-search');

    // The below code should only run on "Create" page
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const query = searchInput.value.toLowerCase();
            document.querySelectorAll('.cost-card').forEach(card => {
                const playerName = card.querySelector('.name').innerText.toLowerCase();
                if (playerName.includes(query)) {
                    card.style.display = 'inline-block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    if (playerButtons){
        playerButtons.forEach(button => {
        
                // Function for adding player to roster
                button.addEventListener('click', () => {
                    // Get player info from clicked button
                    const playerName = button.querySelector('.name').innerText;
                    const playerCost = button.querySelector('.cost-badge').innerText;

                    // Convert budget text and player cost text to int, and deduct money accordingly
                    let costInt = parseInt(playerCost);

                    // Don't allow the addition if funds are insufficient
                    if (remainingMoney - costInt < 0){
                        return;
                    }

                    // Don't allow the addition if name already exists on the team
                    for (let slot of teamSlots){
                        const label = slot.querySelector('.label');
                        if (label.innerText === playerName){
                            return;
                        }
                    }
                    remainingMoney = remainingMoney - costInt;

                    for (let slot of teamSlots) {
                        const status = slot.querySelector('.status');
                        const label = slot.querySelector('.label');

                        if (status.innerText === "Empty") {
                            status.innerText = playerCost;
                            label.innerText = playerName;
                            budget.innerText = remainingMoney.toString();
                            break;
                        }
                    }
            });    
    });
    }

    if (teamSlots){

        // Delete current member upon delete button click if slot is not empty 
        teamSlots.forEach(slot => {
            slot.addEventListener('click', (e) => {
                const target = e.target;
                const status = slot.querySelector('.status');
                if (target.classList.contains('delete')) {
                    // Refund credits if slot is filled
                    if (status.innerText !== "Empty"){
                        const cost = parseInt(status.innerText);
                        remainingMoney += cost;
                        budget.innerText = remainingMoney.toString();
                    }

                    // Change slot labels to empty state
                    const label = slot.querySelector('.label');
                    status.innerText = "Empty";
                    label.innerText = "Player" + " " + slot.id;
                    
                }

            })
        });
    }

    if (createButton){
        createButton.addEventListener('click', () => {
            // Collect all information and send request to Flask for Firestore write
        });
    }
    
    // Attach sidebar pop to all leaderboard team buttons
    const teamButtons = document.querySelectorAll('[id^="button-team"]');
    teamButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove any existing sidebar
            const oldSidebar = document.getElementById('side-bar');
            if (oldSidebar) oldSidebar.remove();
            const teamId = btn.getAttribute('data-team-id');
            fetch(`/api/team/${teamId}`)
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('new');
                    let playersHtml = '';
                    if (data.players && data.players.length > 0) {
                        data.players.forEach((player, idx) => {
                            playersHtml += `<div class='player-card' style='margin:3%'>
                                <div class='label'>${player.gamerTag || player.name || 'Player ' + (idx+1)}</div>`;
                            if (player.seed !== undefined || player.cost !== undefined) {
                                playersHtml += `<div class='status'>`;
                                if (player.seed !== undefined) playersHtml += `Seed: ${player.seed} `;
                                if (player.cost !== undefined) playersHtml += `Cost: ${player.cost}`;
                                playersHtml += `</div>`;
                            }
                            playersHtml += `</div>`;
                        });
                    } else {
                        playersHtml = '<div>No players found for this team.</div>';
                    }
                    const htmlToInsert = `
                        <div class="leaderboard-container" id="side-bar" style="width: 20%; left: 70%; top: 79.5%; height: 120%; justify-content: center;">
                        <button class="link-button" id="x-button" style="color: #ff0000">&times</button>
                        <h2>${data.team_name || 'Team'}</h2>
                        <div class="team-view">
                            ${playersHtml}
                        </div>
                        </div>
                    `;
                    container.insertAdjacentHTML('beforeend', htmlToInsert);
                });
        });
    });
    document.addEventListener("click", function(event) {
        if (event.target.matches("#x-button")) {
            const sideBar = document.getElementById('side-bar');
            if (sideBar) sideBar.remove();
        }
    });

});