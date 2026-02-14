function sortArticles(criterion, order) {
    const container = document.getElementById('articles-container');
    const articles = Array.from(container.getElementsByClassName('article-card'));
    
    // Fonction de tri
    articles.sort((a, b) => {
        let valueA = a.dataset[criterion];
        let valueB = b.dataset[criterion];
        
        // Conversion en nombre si c'est un prix ou une date
        if (criterion === 'price') {
            valueA = parseFloat(valueA);
            valueB = parseFloat(valueB);
        } else if (criterion === 'date') {
            valueA = new Date(valueA);
            valueB = new Date(valueB);
        } else {
            // Pour le texte, conversion en minuscules
            valueA = valueA.toLowerCase();
            valueB = valueB.toLowerCase();
        }
        
        // Comparaison
        if (valueA < valueB) {
            return order === 'asc' ? -1 : 1;
        }
        if (valueA > valueB) {
            return order === 'asc' ? 1 : -1;
        }
        return 0;
    });
    
    // Réorganiser les éléments dans le DOM
    articles.forEach(article => container.appendChild(article));
}