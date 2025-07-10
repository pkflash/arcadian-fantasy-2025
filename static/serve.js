// import { GraphQLClient, gql } from 'graphql-request';

const token = "ea00668ca82bce5c59a8052edd1ea21d";

fetch('https://api.start.gg/gql/alpha', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })


const button1 = document.getElementById('button-team1');
const container = document.getElementById('new');
button1.addEventListener('click', function() {
const htmlToInsert = `
        <div class="leaderboard-container" id="side-bar" style="width: 20%; left: 70%; top: 79.5%; height: 120%; justify-content: center;">
          <button class="link-button" id="x-button" style="color: #ff0000">X</button>
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

// X Button Test
document.addEventListener("click", function(event) {
  if (event.target.matches("#x-button")) {
    const sideBar = document.getElementById('side-bar');
    sideBar.remove();
  }
});

document.addEventListener('DOMContentLoaded', () => {

    const playerButtons = decodeURIComponent.querySelectorAll('.select-player');
    const teamSlots = document.querySelectorAll('.team-player .status');

    playerButtons.forEach(button => {
        button.addEventListener('click', () => {
            const playerName = button.querySelector('.name').innerText;

            for (let slot of teamSlots) {
                if (slot.innerText === "Empty") {
                    slot.innerText = playerName;
                    break;
                }
            }
        })    
    })
})
