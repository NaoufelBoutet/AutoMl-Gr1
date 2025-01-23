
function setupDragAndDrop(dragObjectId, dropZoneId,clonage) {
    const dragObject = document.getElementById(dragObjectId);
    const dropZone = document.getElementById(dropZoneId); 

    // Obtenir les dimensions de la zone de drop
    const positionXzone = dropZone.offsetLeft;
    const positionYzone = dropZone.offsetTop;

    // Gérer le début du drag (dragstart)
    dragObject.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text', e.target.id); // Stocke l'ID de l'élément
        console.log(e.dataTransfer.setData('text', e.target.id))
        e.dataTransfer.effectAllowed = 'copy'; // Autorise la copie
    });

    // Empêche le comportement par défaut pour permettre le drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault(); // Nécessaire pour autoriser le drop
    });

    // Gérer le drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        var listClone = document.getElementsByClassName('clone');
        let nbClone = listClone.length;
        const zoneHeight = parseFloat(window.getComputedStyle(dropZone).getPropertyValue('height'));
        const dragObjectHeight = parseInt(window.getComputedStyle(dragObject).getPropertyValue('height'));
        const dragObjectWidth = parseInt(window.getComputedStyle(dragObject).getPropertyValue('width'));

        // Calculer le décalage
        let adjustX = nbClone * dragObjectHeight;
        let adjustY = dragObjectWidth;
        while (adjustX / zoneHeight > 1) {
            adjustX -= zoneHeight;
            adjustY += dragObjectWidth;
        }

        let positionX = e.clientX;
        let positionY = e.clientY;
        let positionXfinal = positionX - positionXzone;
        let positionYfinal = positionY - positionYzone;

        const id = e.dataTransfer.getData('text'); // Récupère l'ID de l'élément
        const draggedElement = document.getElementById(id);

        const clone = draggedElement.cloneNode(true);
        clone.classList.add('clone'); // Ajoute une classe au clone (si nécessaire)

        // Positionner le clone
        clone.setAttribute("style", `left:${positionXfinal - (adjustX + dragObjectHeight)}px;top:${positionYfinal - adjustY}px;position:relative`);
        clone.setAttribute('Id',`clone${nbClone}`)
        // Ajoute le clone dans la zone de drop
        dropZone.appendChild(clone);
    });
}
document.addEventListener('click', (e)=>{
    let  clickedElement = e.target; 
    let elementId = clickedElement.id;
})
// Appel de la fonction avec des paramètres
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop('object_draggable', 'zone_drag',true);
});

document.addEventListener('DOMContentLoaded', function () {
    const menu_element = document.querySelectorAll('.menu_element');

    menu_element.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault(); // Empêche le lien de naviguer
            const sous_menu = this.nextElementSibling; // Trouve le sous-menu correspondant

            // Toggle pour montrer/masquer le sous-menu
            if (sous_menu.style.display === 'block') {
                sous_menu.style.display = 'none';
            } else {
                sous_menu.style.display = 'block';
            }
        });
    });
});
document.getElementById("delete_btn").addEventListener("click", function() {
    // Afficher la boîte de confirmation
    var confirmation = confirm("Êtes-vous sûr ?");
    
    if (confirmation) {
      // Récupérer la valeur de 'name' et 'value' du bouton
      var actionName = this.getAttribute("name"); // Récupère le 'name' du bouton
      var actionValue = this.getAttribute("value"); // Récupère le 'value' du bouton
      var csrfToken = "{{ csrf_token }}";  // CSRF Token pour la sécurité

      var xhr = new XMLHttpRequest();
      xhr.open("POST", "{% url 'liste_project' %}", true);
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
      xhr.setRequestHeader("X-CSRFToken", csrfToken);

      xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
          // Quand la réponse est reçue avec succès
          document.getElementById("project-info").innerHTML = xhr.responseText;

          // Recharge la page après l'exécution
          location.reload(); // Recharge la page après l'exécution de la fonction
        }
      };

      // Envoyer les données (ici le nom du projet et la valeur de l'action)
      xhr.send(actionName + "=" + actionValue);  // envoyer les valeurs 'name' et 'value' dans la requête
    } else {
      // Si l'utilisateur a annulé, ne rien faire
      console.log("L'utilisateur a annulé l'action.");
    }
  });