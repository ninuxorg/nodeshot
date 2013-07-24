var Imtech = {};
Imtech.Pager = function() {
    this.paragraphsPerPage = 3;
    this.currentPage = 1;
    this.pagingControlsContainer = "#pagingControls";
    this.pagingContainerPath = "#comment";
    
    this.numPages = function() {
        var numPages = 0;
        if (this.paragraphs != null && this.paragraphsPerPage != null) {
            numPages = Math.ceil(this.paragraphs.length / this.paragraphsPerPage);
        }
        
        return numPages;
    };
    
    this.showPage = function(page) {
        this.currentPage = page;
        var html = "";
        for (var i = (page-1)*this.paragraphsPerPage; i < ((page-1)*this.paragraphsPerPage) + this.paragraphsPerPage; i++) {
            if (i < this.paragraphs.length) {
                var elem = this.paragraphs.get(i);
                html += "<" + elem.tagName + ">" + elem.innerHTML + "</" + elem.tagName + ">";
            }
        }
        
        $(this.pagingContainerPath).html(html);
        
        renderControls(this.pagingControlsContainer, this.currentPage, this.numPages());
    }
    
    var renderControls = function(container, currentPage, numPages) {
        var pagingControls = "Page: <ul>";
        for (var i = 1; i <= numPages; i++) {
            if (i != currentPage) {
                pagingControls += "<li><a href='#' onclick='pager.showPage(" + i + "); return false;'>" + i + "</a></li>";
            } else {
                pagingControls += "<li>" + i + "</li>";
            }
        }
        
        pagingControls += "</ul>";
        
        $(container).html(pagingControls);
    }
}