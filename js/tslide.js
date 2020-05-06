/////////
///////////////////////////
///////// Object prototypes 
///////////////////////////
/////////

/////////
///////// Debug object
/////////
/*
    This object provides a straightforward interface for simple debugging --
    mostly entering and exiting functions, printing some state, etc.
*/

function Debug(d) {
    /*
    Print some debugging info to console.

    d.functionName      string      name of function
    d.message           string      message
    d.var               variable    variable to print

    */

    this.functionName   = '<void>';
    this.message        = '<void>';
    this.var            = null;
    this.tab            = 0;

    if (d.constructor == Object) {
        prototype.argcheck(d)
    }

    if(typeof(d) === 'string' || d instanceof String) {
        this.functionName   = d
    }

}

Debug.prototype = {

    constructor:    Debug,

    argcheck:       function (d) {
        if (typeof (d.functionName) != 'undefined')
            this.functionName = d.functionName;
        if (typeof (d.message) != 'undefined')
            this.message = d.message;
        if (typeof (d.var) != 'undefined')
            this.var = d.var;
    },

    cl:             function () {
        console.log(' ');
    },

    indent:         function () {
        str_indent = '';
        for (i = 0; i < this.tab; i++)
            str_indent = str_indent + '\t';
        return str_indent;
    },

    entering:       function () {
        functionCallDepth += 1;
        this.tab = functionCallDepth;
        console.log(
            this.indent()           + 
            '--------> Entering '   + 
            this.functionName       + 
            '...');
    },

    leaving:        function () {
        console.log(
            this.indent()       + 
            'Leaving '          + 
            this.functionName   + 
            ' --------> ');
        functionCallDepth -= 1;
    },

    vlog:           function (d) {
        this.argcheck(d);
        if (typeof (this.var) === 'object') {
            console.log(
                this.indent()               + 
                'In ' + this.functionName   + 
                ': ' + d.message + ' = '
            );
            console.log(d.var);
        } else
            console.log(
                this.indent()               + 
                'In ' + this.functionName   + 
                ': ' + d.message    + ' = ' + d.var);
    },

    log:            function (d) {
        this.argcheck(d);
        console.log(
                this.indent()               + 
                'In ' + this.functionName + ': ' + d.message);
    }

}

/////////
///////// DOM object
/////////

function DOM(al_keylist) {
    this.str_help = `

        This object provides a convenient abstraction
        for accessing and interacting with named components 
        of the DOM, removing the very tight coupling that 
        might occur by referening DOM literals directly in JS.
    
    `;
    this.l_DOM = al_keylist;
}

DOM.prototype = {
    constructor:    DOM,

    elements:           function() {
        return this.l_DOM;
    },

    get:                function(str_key) {
        if(this.l_DOM.includes(str_key)) {
            return $('#'+str_key).val()
        } else {
            return null;
        }
    },

    html:               function(str_key, str_val) {
        if(this.l_DOM.includes(str_key)) {
            $('#'+str_key).html(str_val)
        }
    },

    innerHTML_listadd:  function(str_key, l_val) {
        if(this.l_DOM.includes(str_key)) {
            for(const str_line of l_val) {
                document.getElementById(str_key).innerHTML += str_line;
            }
        }
    },

    innerHTML_listset:  function(str_key, l_val) {
        if(this.l_DOM.includes(str_key)) {
            document.getElementById(str_key).innerHTML = '';
            for(const str_line of l_val) {
                document.getElementById(str_key).innerHTML += str_line;
            }
        }
    },

    style_set:          function(str_key, d_style) {
        if(this.l_DOM.includes(str_key)) {
            for(const [key, value] of Object.entries(d_style)) {
                document.getElementById(str_key).style[key] = value;
            }
        }
    },

    type_set:           function(str_key, typeSet) {
        if(this.l_DOM.includes(str_key)) {
            document.getElementById(str_key).type = typeSet;
        }
    },

    set:                function(str_key, str_val) {
        if(this.l_DOM.includes(str_key)) {
            $('#'+str_key).val(str_val)
            return $('#'+str_key).val();
        } else {
            return null;
        }
    }
}

/////////
///////// URL object
/////////

function URL(dom) {
    this.str_help   = `

        This object parses the URL for parameters to set in the 
        dashboard.

    `;
    this.dom        = dom;
    this.str_query  = window.location.search;
    this.urlParams  =  new URLSearchParams(this.str_query);
}

URL.prototype = {
    constructor:    URL,

    parse:          function() {
        this.dom.elements().forEach(el => {
            if(this.urlParams.has(el)) {
                this.dom.set(el, this.urlParams.get(el));
            }
        })
    }
}

/////////
///////// A Page object that describes the HTML version elements from a 
///////// logical perspective.
/////////

function Page() {
    this.str_help = `

        The Page object defines/interacts with the html page.

        The page element strings are "defined" here, and letious
        DOM objects that can interact with these elements are also
        instantiated.
        
    `;

    this.currentSlide               = 1;
    document.onkeydown              = this.checkForArrowKeyPress;


    // Keys parsed from the URL
    this.l_urlParamsBasic = [   
        "slide", 
    ];

    // DOM keys related to the slides
    this.l_slide                = [];   // Simple index of DOMslideIDs
    this.l_snippetsPerSlide     = [];   // Number of snippets per slide
    this.l_snippetPerSlideON    = [];   // Running count of ON snippets
    this.str_slideIDprefix      = "";
    this.init();

    // DOM obj elements --  Each object has a specific list of page key
    //                      elemnts that it process to provide page
    //                      access functionality
    this.DOMurl         = new DOM(this.l_urlParams);
    this.DOMslide       = new DOM(this.l_slide);
    // object that parses the URL
    this.url            = new URL(this.DOMurl);

}

Page.prototype = {
    constructor:    Page,

    substr_count:                       function(astr_substr, astr_text) {
        let str_help = `
            Count and return the occurences of a substring in a string.
        `;
        return (astr_text.match(new RegExp(astr_substr, 'gi')) || []).length;
    },

    init:                               function() {
        let str_help = `
            Initialize some member variables based on meta data
            in the DOM.
        `;

        this.str_slideIDprefix  = document.getElementById('slideIDprefix').innerHTML;
        let numberOfSlides      = document.getElementById('numberOfSlides').innerHTML;
        for(let i=1; i<=numberOfSlides; i++) {
            this.l_slide.push(this.str_slideIDprefix + i);
        }

        // Parse for snippets per slide
        for(const DOMslideID of this.l_slide) {
            str_slide           = document.getElementById(DOMslideID).outerHTML;
            snippetsPerSlide    = this.substr_count('snippet', str_slide);
            this.l_snippetsPerSlide.push(snippetsPerSlide);
            this.l_snippetPerSlideON.push(0);
        }
    },

    retreat_overSnippets:               function() {
        let str_help = `
            For a given slide, this retreats over the snippets, turning 
            each current snippet OFF. 

            Return:
            true:       All snippets have been toggled to display: none
            false:      Some snippets still ON
        `;
        let thisSlide   = this.currentSlide-1
        // Check if all snippets are OFF, and if so, return with a true
        if(this.l_snippetPerSlideON[thisSlide] == 0)
            return true;

        let snippetToDisplayOFF         = this.l_snippetPerSlideON[thisSlide];
        let DOMsnippet                  = document.getElementById(
                                            'order-' + this.currentSlide + 
                                            '-' + snippetToDisplayOFF
                                            );
        DOMsnippet.style.display        = 'none';
        this.l_snippetPerSlideON[thisSlide] -= 1;
        return false;
        
    },

    advance_overSnippets:               function() {
        let str_help = `
            For a given slide, this advances over the snippets, turning
            each current snippet ON.

            Return:
            true:       All snippets have been toggled to display: block
            false:      Some snippets still OFF
        `;
        let thisSlide   = this.currentSlide-1
        // Check if all snippets are ON, and if so, return with a true
        if(this.l_snippetPerSlideON[thisSlide] == 
            this.l_snippetsPerSlide[thisSlide]) 
            return true;

        let snippetToDisplay            = this.l_snippetPerSlideON[thisSlide] + 1;
        let DOMsnippet                  = document.getElementById(
                                                'order-' + this.currentSlide +
                                                '-' + snippetToDisplay
                                            );
        DOMsnippet.style.display    = 'block';
        this.l_snippetPerSlideON[thisSlide]    += 1;
        return false;
    },

    allSnippets_displaySet:             function(astr_state, a_slideIndex) {
        let str_help = `
            For a given slide <a_slideIndex> set the display state of (any)
            snippet elements to <astr_state>. Note that the <a_slideIndex>
            counts starting from 1 not 0.
        `;
        snippets    = this.l_snippetsPerSlide[a_slideIndex-1];
        for(let snippet=1; snippet <= snippets; snippet++) {
            DOMsnippet = document.getElementById(
                            'order-' + a_slideIndex +
                            '-' + snippet
            );
            DOMsnippet.style.display =  astr_state;
        }
        this.l_snippetPerSlideON[a_slideIndex-1] = 0;
    },

    advance_toFirst:                    function() {
        let str_help = `
            Advance to first slide...
        `;
        let index_currentSlide      = this.currentSlide;
        let index_followingSlide    = 1;
        this.currentSlide           = index_followingSlide;
        this.slide_transition(index_currentSlide, index_followingSlide);
    },

    advance_toLast:                     function() {
        let str_help = `
            Advance to last slide...
        `;
        let index_currentSlide      = this.currentSlide;
        let index_followingSlide    = this.l_slide.length;
        this.currentSlide           = index_followingSlide;
        this.slide_transition(index_currentSlide, index_followingSlide);
    },

    advance_toNext:                     function() {
        let str_help = `
            Advance to next slide...
        `;
        let index_currentSlide      = this.currentSlide;
        let index_followingSlide    = index_currentSlide+1;
        if(index_followingSlide > this.l_slide.length) {
            index_followingSlide    = 1;
        } 
        this.currentSlide           = index_followingSlide;
        this.slide_transition(index_currentSlide, index_followingSlide);
    },

    advance_toPrevious:                 function() {
        let str_help = `
            Advance to previous slide...
        `;
        let index_currentSlide      = this.currentSlide;
        let index_followingSlide    = index_currentSlide-1;
        if(index_followingSlide < 1) {
            index_followingSlide    = this.l_slide.length;
        } 
        this.currentSlide           = index_followingSlide;
        this.slide_transition(index_currentSlide, index_followingSlide);
    },

    slide_transition:                   function(index_currentSlide, 
                                                 index_followingSlide) {
        let str_help = `
            Do the actual transition from one slide to another, 
            as well as update the running slide counter in the footer.

            Also, on the next slide, all 'snippets' are set to 'none'.
        `;

        let DOMID_currentSlide      = document.getElementById(
                                            this.str_slideIDprefix + index_currentSlide
                                        );
        let DOMID_followingSlide    = document.getElementById(
                                            this.str_slideIDprefix + index_followingSlide
                                        );
        let DOMID_slideTitle        = document.getElementById(
                                            this.str_slideIDprefix + index_followingSlide + 
                                            '-title');
        let DOMID_slideCounter      = document.getElementById('slideCounter');
        let DOMID_pageTitle         = document.getElementById('pageTitle');
        let DOMID_slideBar          = document.getElementById('slideBar');

        DOMID_currentSlide.style.display    = "none";
        DOMID_followingSlide.style.display  = "block";
        // this.allSnippets_displaySet('none', index_followingSlide);
        if(DOMID_slideTitle !== null) {
            DOMID_pageTitle.innerHTML = DOMID_slideTitle.innerHTML;
        } else { 
            DOMID_pageTitle.innerHTML = " ";
        }
        DOMID_slideCounter.innerHTML = "slide "                 +
                                        this.currentSlide       + 
                                        " / " + this.l_slide.length;
        progress = this.currentSlide / this.l_slide.length * 100;
        DOMID_slideBar.style.width = progress + "%";
    },

    // Page
    FAinputButton_create:               function(astr_functionClickName, 
                                                 astr_value, 
                                                 astr_fname, 
                                                 astr_baseSet = "fa") {
        let str_inputButton     = `<input type="button"   onclick="` + astr_functionClickName + `"
                                    value=" &#x` + astr_value + ` " 
                                    style="padding: .1em .4em;" 
                                    class=" pure-button 
                                            pure-button-primary 
                                            ` + astr_baseSet + ` ` + astr_baseSet + '-' + astr_fname + `">
                                  `;
        return(str_inputButton);
    },

    // Page
    rightArrow_inputButtonCreate:       function() {
        return(this.FAinputButton_create("page.rightArrow_process()", 
                                         "f35a", "arrow-alt-circle-right"));
    },

    // Page
    rightArrow_process:                 function() {
        let str_help = `

            Process a right arrow event

            Call the next slide.

        `;

        if(this.advance_overSnippets())
            this.advance_toNext();
    },

    // Page
    leftArrow_inputButtonCreate:        function() {
        return(this.FAinputButton_create("page.leftArrow_process()",
                                         "f359", "arrow-alt-circle-left"));
    },

    // Page
    leftArrow_process:                  function() {
        let str_help = `

            Process a left arrow event

            Call the previous slide.
        `;
        if(this.retreat_overSnippets())
            this.advance_toPrevious();
    },

    // Page
    upArrow_inputButtonCreate:          function() {
        return(this.FAinputButton_create("page.upArrow_process()",
                                         "f35b", "arrow-alt-circle-up"));
    },

    // Page
    upArrow_process:                    function() {
        let str_help = `

            Process an up arrow event -- 

            Call the first slide.

        `;

        this.advance_toFirst();
    },

    // Page
    downArrow_inputButtonCreate:        function() {
        return(this.FAinputButton_create("page.downArrow_process()",
                                         "f358", "arrow-alt-circle-down"));
    },

    // Page
    downArrow_process:                  function() {
        let str_help = `

            Process a down arrow event

            Call the final slide.
        `;

        this.advance_toLast();
    },

    // Page
    checkForArrowKeyPress:          function(e) {
        let str_help = `

            The 'this' seems confused at this point. My guess is that
            since the event is defined on the "document" the 'this' 
            retains that identify when executing here. 

            Hence, we call the 'page' variable explicitly when resolving
            scope.

        `;

        e = e || window.event;

        if (e.keyCode == '38') {
            // up arrow
            console.log('up arrow')
            page.upArrow_process();
        }
        else if (e.keyCode == '40') {
            // down arrow
            console.log('down arrow')
            page.downArrow_process();
        }
        else if (e.keyCode == '37') {
           // left arrow
           console.log('left arrow')
            page.leftArrow_process();
        }
        else if (e.keyCode == '39') {
           // right arrow
           console.log('right arrow')
            page.rightArrow_process();
        }
    },

    
    // Page
    fields_populateFromURL: function() {
        let str_help = `
            Populate various fields on the page from URL args
        `;
        this.url.parse();
    }
}

// ---------------------------------------------------------------------------------------------------------------
// ---------------------------------------------------------------------------------------------------------------

// Page object
let page            = new Page();


// The whole document
$body                       = $("body");

window.onload = function() {
    // Start on the first slide
    page.advance_toFirst();
};

