// const button1 = document.getElementById('button-team1');
const TOTAL_COST = 1200;
let remainingMoney = TOTAL_COST;
const createButton = document.getElementById('Register');
// Button1 check only passes on index page
// if (button1){
//     button1.addEventListener('click', function() {
//         const container = document.getElementById('new');
//         const htmlToInsert = `
//                 <div class="leaderboard-container" id="side-bar" style="width: 20%; left: 70%; top: 79.5%; height: 120%; justify-content: center;">
//                 <button class="link-button" id="x-button" style="color: #ff0000">&times</button>
//                 <h2>Gang Bangers of All Time</h2>
//                 <div class="team-view">
//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 1</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 2</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 3</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 4</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 5</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 6</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 7</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 8</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 9</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 10</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 11</div>
//                         <div class="status">Empty</div>
//                     </div>

//                     <div class="player-card" style="margin: 3%">
//                         <div class="label">Player 12</div>
//                         <div class="status">Empty</div>
//                     </div>
//                 </div>
//                 </div>
//         `;
//         container.insertAdjacentHTML('beforeend', htmlToInsert);
//         });
    
//     document.addEventListener("click", function(event) {
//         if (event.target.matches("#x-button")) {
//         const sideBar = document.getElementById('side-bar');
//         sideBar.remove();
//     }
//     });
// }


document.addEventListener('DOMContentLoaded', function() {
    // --- Player selection and team creation logic for create team page ---
    const teamForm = document.getElementById('team-form');
    if (teamForm) {
        const BUDGET_LIMIT = 1200;
        let players = [];
        let currentBudget = BUDGET_LIMIT;

        function updateBudgetDisplay() {
            const budgetElem = document.querySelector('.budget-box .amount h3');
            if (budgetElem) budgetElem.textContent = currentBudget;
        }

        let budgetErrorTimeout = null;
        function showBudgetError(show) {
            const errElem = document.getElementById('budget-error');
            if (show) {
                errElem.style.display = 'block';
                if (budgetErrorTimeout) clearTimeout(budgetErrorTimeout);
                budgetErrorTimeout = setTimeout(() => {
                    errElem.style.display = 'none';
                }, 5000); // Show for 5 seconds
            } else {
                errElem.style.display = 'none';
                if (budgetErrorTimeout) clearTimeout(budgetErrorTimeout);
            }
        }

        const playerButtons = document.querySelectorAll('.cost-card');
        playerButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const playerId = btn.getAttribute('data-entrant-id');
                const gamerTag = btn.getAttribute('data-gamertag');
                const seed = btn.getAttribute('data-seed');
                const cost = btn.getAttribute('data-cost');
                const isSelected = btn.classList.contains('selected');
                if (!isSelected) {
                    if (players.length >= 12) {
                        showBudgetError(true);
                        return;
                    }
                    if (currentBudget - parseInt(cost) < 0) {
                        showBudgetError(true);
                        return;
                    }
                    players.push({
                        id: playerId,
                        gamerTag: gamerTag,
                        seed: seed,
                        cost: cost
                    });
                    console.log('DEBUG: players after add:', players);
                    currentBudget -= parseInt(cost);
                    btn.classList.add('selected');
                    showBudgetError(false);
                } else {
                    // Deselect
                    players = players.filter(p => p.id !== playerId);
                    console.log('DEBUG: players after remove:', players);
                    currentBudget += parseInt(cost);
                    btn.classList.remove('selected');
                    showBudgetError(false);
                }
                updateBudgetDisplay();
            });
        });

        teamForm.addEventListener('submit', function(e) {
            // Collect selected player objects
            const playersInput = document.getElementById('players-input');
            console.log('DEBUG: players before submit:', players);  // Debug print
            playersInput.value = JSON.stringify(players);
            console.log('DEBUG: playersInput.value after JSON.stringify:', playersInput.value);  // Debug print
        });
    }

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
            const teamId = btn.getAttribute('data-team-id');
            const oldSidebar = document.getElementById('side-bar');
            // If sidebar is open for this team, close it (toggle)
            if (oldSidebar && oldSidebar.getAttribute('data-team-id') === teamId) {
                oldSidebar.remove();
                return;
            }
            // Remove any existing sidebar before inserting a new one
            if (oldSidebar) oldSidebar.remove();
            fetch(`/api/team/${teamId}`)
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('new');
                    // Remove any sidebar again just before inserting (double safety)
                    const checkSidebar = document.getElementById('side-bar');
                    if (checkSidebar) checkSidebar.remove();
                    let playersHtml = '';
                    if (data.players && data.players.length > 0) {
                        data.players.forEach((player, idx) => {
                            playersHtml += `<div class='player-card' style='margin:3%'>
                                <div class='label'>${player.gamerTag || player.name || 'Player ' + (idx+1)}</div><br>`;
                            if (player.seed !== undefined || player.cost !== undefined) {
                                playersHtml += `<div class='status'>`;
                                if (player.seed !== undefined) playersHtml += `Seed: ${player.seed}<br>`;
                                if (player.cost !== undefined) playersHtml += `Cost: ${player.cost}<br>`;
                                playersHtml += `</div>`;
                            }
                            playersHtml += `</div>`;
                        });
                    } else {
                        playersHtml = '<div>No players found for this team.</div>';
                    }
                    const htmlToInsert = `
                        <div class="leaderboard-container" id="side-bar" data-team-id="${teamId}">
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

    // Leaderboard search bar filter
    const leaderboardSearch = document.getElementById('leaderboard-search');
    if (leaderboardSearch) {
        leaderboardSearch.addEventListener('input', function() {
            const query = leaderboardSearch.value.toLowerCase();
            const rows = document.querySelectorAll('.leaderboard-container table tr');
            rows.forEach((row, idx) => {
                // Skip header row
                if (idx === 0) return;
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    // Fade out flash message after 5 seconds
    var flash = document.getElementById("flash-message");
    if (flash) {
        setTimeout(function() {
            flash.classList.add("fade-out");
            setTimeout(function() {
                flash.style.display = "none";
            }, 1000); // match the animation duration
        }, 5000); // 5 seconds before starting fade
    }

});