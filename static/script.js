
/* Sélection du bouton et de l'élément par leur ID
const button = document.getElementById('my-button');
const element = document.getElementById('my-element');

// Ajout d'un écouteur d'événements pour le clic sur le bouton
button.addEventListener('click', function() {
  // Envoi d'une requête HTTP au serveur lorsque le bouton est cliqué
  fetch('/click')
    .then(response => response.text())
    .then(data => {
      // Affichage de la réponse du serveur dans l'élément HTML
      element.textContent = data;
      console.log(response.text);
      console.log(data);
    });
});*/

import Alpine from "https://cdn.skypack.dev/alpinejs@3.11.1";

//Demo variables
const mockTypingAfter = 1500;
const mockResponseAfter = 3000;
const mockOpeningMessage =
  "Bonjour ! Je suis CineMate, votre assistant virtuel pour les recommendantions cinéma. <br>Pour commencer, quel est votre film préféré ?";
const mockResponsePrefix = "Votre message: ";

document.addEventListener("alpine:init", () => {
  Alpine.data("chat", () => ({
    newMessage: "",
    mockres: "",
    step: 1,
    showTyping: false,
    waitingOnResponse: true,
    messages: [],
    init() {
      this.mockResponse(mockOpeningMessage);
    },
    sendMessage() {
      if (this.waitingOnResponse) return;
      this.waitingOnResponse = true;
      this.messages.push({ role: "user", body: this.newMessage });
      this.newMessage = "";
      //window.scrollTo(0, 0); //To fix weird iOS zoom on input
      
      //message string to obj
      let userMessage = this.messages[this.messages.length - 1].body;
      console.log(this.step);
      let userMessageobj = {message: userMessage, step: this.step};
      console.log(this.step);

      //send message to flask
      fetch('/userMessage',{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userMessageobj) //obj to json
      })
        .then(response => response.json())
        .then(data => {
          // Affichage de la réponse du serveur dans l'élément HTML
          console.log(this.mockres);
          console.log(this.step);
          if (this.step == 1){
            console.log(data)
            if(data.length === 0){
              this.mockres = "Aucun film trouvé !<br> Veuillez réessayer."
              this.step= 0;
              }
              else{
                this.mockres = "Voici les films trouvés:<br><br>";
              
                for (let i = 0; i < data.length; i++) {
                  let movie = data[i];
                  this.mockres += `${i + 1}. ${movie.title}`;
                  if(movie.release_date != null){
                  this.mockres += `(${movie.release_date})`;
                  }
                  this.mockres += `<br>`;
                }
                this.mockres += `<br>Sélectionnez le numéro du film que vous voulez choisir (ou tapez '0' pour annuler)`;
                console.log(this.mockres);
            }
          }

        if(this.step == 2 ){
          console.log(data);
          if (data["choice"]==0){
            this.mockres = "Selection annulée, Quel est votre film préféré ?";
            this.step = 0;
          } else if (data["invalide"] == "invalide"){
            this.mockres = "Choix invalide. Veuillez sélectionner un numéro de film valide.";
            this.step = 1;
          }else{
            this.mockres = "Quel est le dernier film que Vous avez bien aimé ?"
          }
        }

        if(this.step == 3){
          if(data.length === 0){
            this.mockres = "Aucun film trouvé !<br> Veuillez réessayer."
            this.step= 0;
            }
            else{
              this.mockres = "Voici les films trouvés:<br><br>";
            
              for (let i = 0; i < data.length; i++) {
                let movie = data[i];
                this.mockres += `${i + 1}. ${movie.title}`;
                if(movie.release_date != null){
                this.mockres += `(${movie.release_date})`;
                }
                this.mockres += `<br>`;
              }
              this.mockres += `<br>Sélectionnez le numéro du film que vous voulez choisir (ou tapez '0' pour annuler)`;
              console.log(this.mockres);
          }
        }
          console.log(this.step);
          console.log(data);
          console.log(this.mockres);
          this.mockResponse(this.mockres);
          this.step++;
        });
    },
    typeOutResponse(message) {
      this.messages.push({ role: "assistant", body: "", beingTyped: true });
      let responseMessage = this.messages[this.messages.length - 1];
      let i = 0;
      let interval = setInterval(() => {
        responseMessage.body += message.charAt(i);
        i++;
        window.scrollTo(0, document.body.scrollHeight);
        if (i > message.length - 1) {
          this.waitingOnResponse = false;
          delete responseMessage.beingTyped;
          clearInterval(interval);
        }
      }, 30);
    },
    mockResponse(message) {
      setTimeout(() => {
        this.showTyping = true;
      }, mockTypingAfter);
      setTimeout(() => {
        this.showTyping = false;
        let responseMessage =
          message ??
          mockResponsePrefix + this.messages[this.messages.length - 1].body;
        console.log(message);
        this.typeOutResponse(responseMessage);
      }, mockResponseAfter);
    }
  }));
});

Alpine.start();




