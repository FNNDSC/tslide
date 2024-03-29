# System imports
import      os
import      getpass
import      argparse
import      json
import      pprint
import      re
import      logging

import      hjson
import      glob
import      io

from        distutils.dir_util  import  copy_tree

# Imports for the "fortune" auto-generating
import      fortune
import      cowsay
from        cowpy               import cow
from        pyfiglet            import Figlet
# cowsay.tux(f.renderText(fortune.get_random_fortune('./fortunes')))

# Project specific imports
import      pfmisc
from        pfmisc._colors      import  Colors
from        pfmisc              import  other
from        pfmisc              import  error

import      pudb
from        pfstate             import  S
from        pfmisc.C_snode      import  C_snode

class D(S):
    """
        A derived 'pfstate' class that keeps some system state
        variables in a tree SNode structure.
    """

    def __init__(self, *args, **kwargs):
        """
            Constructor for the state object.

            This might be overkill for this module.
        """

        for k,v in kwargs.items():
            if k == 'args':     d_args          = v

        S.__init__(self, *args, **kwargs)
        if not S.b_init:
            d_specific  = \
                {
                    "slideMeta": {
                        'cowsaycharacters': [
                            'beavis',
                            'cheese',
                            'daemon',
                            'cow',
                            'dragon',
                            'ghostbusters',
                            'kitty',
                            'meow',
                            'milk',
                            'stegasaurus',
                            'stimpy',
                            'turkey',
                            'turtle',
                            'tux'
                        ],
                        'htmlComponents': {
                            'doctype':  {
                                'file':     'doctype.html',
                                'contents': ''
                            },
                            'head':     {
                                'file':     'head.html',
                                'contents': ''
                            },
                            'navbar':   {
                                'file':     'navbar.html',
                                'contents': ''
                            },
                            'logos':   {
                                'file':     'logos.html',
                                'contents': ''
                            },
                            'title':   {
                                'file':     'title.html',
                                'contents': ''
                            },
                            'body':     {
                                'file':     'body.html',
                                'contents': ''
                            },
                            'footer':   {
                                'file':     'footer.html',
                                'contents': ''
                            },
                        },
                        'dirComponents': {
                            'html':         './html',
                            'logos':        './logos',
                            'images':       './images',
                            'css':          './css',
                            'javascript':   './js',
                            'fortunes':     './fortunes'
                        }
                    }
                }
            S.d_state.update(d_specific)
            S.T.initFromDict(S.d_state)
            S.b_init    = True
            if len(S.T.cat('/this/debugToDir')):
                if not os.path.exists(S.T.cat('/this/debugToDir')):
                    os.makedirs(S.T.cat('/this/debugToDir'))

        self.dp.qprint(
            Colors.YELLOW + "\n\t\tInternal data tree:",
            level   = 1,
            syslog  = False)
        self.dp.qprint(
            C_snode.str_blockIndent(str(S.T), 3, 8),
            level   = 1,
            syslog  = False)

class SMarkDown(object):
    """
        The directive for markdown is a markdown marker string,
        followed by a "function" string followed by optional
        "args" for that function. The arguments are separated
        by commas. The remainder of the string line is taken to be
        the string to which apply the markdown.

        So, markdown patterns are:

            <mdMarker><mdFunction>_<mdArg1>,<mdArg2>,...<mdArgN> string

        for example:

        _#_o_1 bullet 1 : create a snippet of "ordering" 1, with text 'bullet 1'
        _#_o_2 bullet 2 : create a snippet of "ordering" 2, with text 'bullet 2'

        Args for bullet points:

            _#_o_<N>,<HTMLStyle>,<tabPadding>

            <N>             bullet ordering. Must be unique on a slide;
                            multiple bullets with the same order <N> will
                            crash the browser.

            <HTMLStyle>     a quoted string that will be added to each
                            snippet line. The following macros are understood:
                            'l':    'style="float: left;"'
                            'r':    'style="float: right;"

            <tabPadding>    Optionally pre-pad the bullet with multiples of
                            8 space chars.


        _#_font_<figletFont> text : Render <text> with <figletFont>.
        See http://www.jave.de/figlet/fonts/overview.html for figlet fonts.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor, basically set some internal vars.
        """
        self.__name__           = 'SMarkDown'
        self.verbosityLevel     = 1
        self.mdMarker           = "_#_"
        self.dp                         = pfmisc.debug(
                                            verbosity   = self.verbosityLevel,
                                            within      = self.__name__
                                            )

    def snippetMake(self, al_argList, astr_text):
        """
            Replace the <astr_text> with the relevant snippet equivalent.
        """
        d_ret   = {
            'status':   True,
            'result':   "",
            'error':    ""
        }

        def args_parse(al_argList):
            """
                Parse the snippet argument list. Snippet arguments conform
                to the following pattern:

                    <key1>~<value1>,<key2>~<value2>,...

                where the following keys are understood:

                    b~<N>           bullet ordering, i.e.   b~01, b~02, ...
                                    Note that bullet ordering is the only
                                    argument that does not require the
                                    preceding "b~" -- see below.
                    f~<floatStyle>  HTML text for the float style
                                        f~l     == "float: left;"
                                        f~r     == "float: right;"
                    t~<tabs[<width>> number of tabs to insert before bullet
                                        and optional [<width>
                                        t~4     == 4 tabs (width 8)
                                        t~4[2   == 4 tabs (width 2)
                    z~<font-size>   font-size style specifier
                                        z~150%  == "font size: 150%;"

                Note that the ordering key~value is the only pairing where
                only a value can be provided and the key is assumed to
                be the bullet ordering. In other words, the following are
                equivalent source specifications for a snippet order:

                    _#_o_01
                    _#_o_b~01

            """
            d_ret = {
                'order':    0,
                'style':    "",
                'padding':  ""
            }
            tabWidth    = 8
            str_style   = ""
            for arg in al_argList:
                try:
                    (key, val)  = arg.split('~')
                except:
                    d_ret['order'] = int(arg)
                    continue
                if key == 'b':
                    d_ret['order']  = int(val)
                    continue
                if key == 'f':
                    str_style   += "float: " + "left;" if val == 'l' else "right;"
                    continue
                if key == 't':
                    try:
                        (tab, width) = val.split('[')
                        tabWidth    = width
                    except:
                        tab = val
                    d_ret['padding'] = " " * int(tab) * tabWidth
                    continue
                if key == 'z':
                    str_style   += "font-size: %s" % val + ";"
            d_ret['style'] = 'style= "' + str_style + '"'
            return d_ret


        d_context       = args_parse(al_argList)
        d_ret['result'] += '''<br><div class = "snippet" id="order-''' + str(d_context['order']) + '''" ''' +d_context['style']+'''><pre>''' + d_context['padding']  + astr_text + '''</pre></div>'''

        return d_ret

    def fontify(self, al_argList, astr_text):
        """
            Replace the <astr_text> with a figlet font of the same.
            If invalid font, then return the astr_text unchanged.
        """
        d_ret   = {
            'status':   False,
            'result':   "",
            'error':    ""
        }
        str_font    = al_argList[0]
        try:
            f               = Figlet(font=str_font)
            astr_text       = f.renderText(astr_text)
            d_ret['status'] = True
            d_ret['result'] = astr_text
        except Exception as e:
            d_ret['error']  = str(e) + " font not found"

        return d_ret

    def cowpy(self, al_argList, astr_text):
        """
            Place the <astr_text> in a "cowpy" bubble with an
            optional character spec. Default character is 'tux'.

        """
        d_ret   = {
            'status':   False,
            'result':   "",
            'error':    ""
        }
        if len(al_argList):
            str_char        = al_argList[0]
        else:
            str_char        = 'moose'
        try:
            if str_char != 'random':
                cow_cls         = cow.get_cow(str_char)
                betsy           = cow_cls()
                d_ret['result'] = betsy.milk(astr_text)
            else:
                d_ret['result'] = cow.milk_random_cow(astr_text)
            d_ret['status'] = True
        except Exception as e:
            d_ret['error']  = str(e) + " character not found"

        return d_ret

    def lineWidthBound(self, al_argList, astr_text):
        """
            Hard limit the <astr_text> to only the first
            <length> characters
        """
        d_ret   = {
            'status':   False,
            'result':   "",
            'error':    ""
        }
        length              = int(al_argList[0])
        try:
            astr_text       = astr_text[:length]
            d_ret['status'] = True
            d_ret['result'] = astr_text
        except Exception as e:
            d_ret['error']  = str(e) + " line limit failed"

        return d_ret

    def markdown_process(self, astr_commandArg, astr_text):
        """
            Process the markdown by calling the appropriate
            handler on the text
        """
        d_ret = {
            'status':   False,
            'result':   "",
            'error':    "",
        }
        l_markdownComArg    = astr_commandArg.split('_')
        str_command         = l_markdownComArg[0]
        l_argList           = l_markdownComArg[1].split(',')
        if str_command == 'o':
            d_ret['status']     = True
            d_ret['d_result']   = self.snippetMake(l_argList, astr_text)
        if str_command == 'font':
            d_ret['status']     = True
            d_ret['d_result']   = self.fontify(l_argList, astr_text)
        if str_command == 'cowpy':
            d_ret['status']     = True
            d_ret['d_result']   = self.cowpy(l_argList, astr_text)
        if str_command == 'w':
            d_ret['status']     = True
            d_ret['d_result']   = self.lineWidthBound(l_argList, astr_text)

        return d_ret

    def markdown_do(self, astr_line):
        """
            Process the markdown directive in the <astr_line> and
            branch to appropriate handler.
        """
        d_ret       = {
            'status':       False,
            'd_markdown':   {}
        }
        # split astr_line into a list and find the element
        # containing the this.mdMarker
        l_words     = astr_line.split()
        for str_word in l_words:
            if self.mdMarker in str_word:
                str_commandArg      = str_word.split(self.mdMarker)[1]
                str_text            = astr_line.split(str_word)[1]
                d_ret['d_markdown'] = self.markdown_process(str_commandArg, str_text)
                d_ret['status']     = True
                break
        return d_ret

    def run(self, astr_body):
        """
            Parse the <astr_body> for certain markdown
            and replace with suitable HTML, which is
            returned.
        """
        # Split the input <astr_body> into an array of lines
        l_lines     = astr_body.split("\n")
        l_newLines  = []

        # find and process lines that contain the markdown marker
        for str_line in l_lines:
            if self.mdMarker in str_line:
                d_do        = self.markdown_do(str_line)
                if d_do['status']:
                    if d_do['d_markdown']['status']:
                        if d_do['d_markdown']['d_result']['status']:
                            str_line    = d_do['d_markdown']['d_result']['result']
                        else:
                            self.dp.qprint('Error returned:\n%s' % \
                                            json.dumps(d_do, indent=4),
                                            comms = 'error')
            l_newLines.append(str_line)
        str_body    = '\n'.join(l_newLines)
        return str_body

class tsmake(object):
    """
    The 'tsmake' class provides the workhose methods for the tsmake
    operational script.

    """

    _dictErr = {
        'outputDirFail'   : {
            'action'        : 'trying to check on the output directory, ',
            'error'         : 'directory not specified. This is a *required* input',
            'exitCode'      : 1
        },
        'inputDirFail'   : {
            'action'        : 'trying to check on the input directory, ',
            'error'         : 'directory not found. This is a *required* input',
            'exitCode'      : 1
        },
    }

    def declare_selfvars(self, *args, **kwargs):
        """
        A block to declare self variables
        """

        def outputDir_process(str_outputDir):
            if str_outputDir == '%inputDir':
                self.str_outputDir  = self.str_inputDir
            else:
                self.str_outputDir  = str_outputDir

        #
        # Object desc block
        #
        self.args                               = kwargs
        self.__name__                           = "tsmake"

        # Init some vars
        self.b_noLogos                          = False
        self.str_additionalDirList              = ""

        # Parse CLI args
        for key, value in kwargs.items():
            if key == 'inputDir':           self.str_inputDir           = value
            if key == "outputDir":          outputDir_process(value)
            if key == 'b_noPageSplit':      self.b_noPageSplit              = value
            if key == 'verbosity':          self.verbosityLevel         = int(value)
            if key == 'b_noLogos':          self.b_noLogos              = bool(value)
            if key == 'fortune':            self.fortuneSlides          = int(value)
            if key == 'slidePrefixDOMID':   self.str_slidePrefixDOMID   = value
            if key == 'slideListGlob':      self.str_slideListGlob      = value
            if key == 'slideTextNumRows':   self.textNumRows            = int(value)
            if key == 'slidesFile':         self.str_slidesFile         = value
            if key == 'slidesFileBreak':    self.str_slidesFileBreak    = value
            if key == 'additionalDirList':  self.str_additionalDirList  = value

        # Slide lists and dictionaries
        self.lstr_slideFiles                    = []
        self.ld_slide                           = []
        self.str_extension                      = "hjson"

        #----------------- state --------------------
        # There are some implicit assumptions in the
        # underlying pfstate module that need to be
        # addressed in future versions of that module
        self.args['args']                       = {}
        self.args['args']['str_configFileLoad'] = ''
        self.args['args']['str_configFileSave'] = ''
        self.args['args']['str_debugToDir']     = '/tmp'
        self.args['args']['verbosity']          = self.args['verbosity']
        self.state                              = D(**self.args)
        self.data                               = self.state.T

        # pftree dictionary
        self.pf_tree                            = None
        self.numThreads                         = 1

        # Some output handling
        self.str_stdout                         = ''
        self.str_stderr                         = ''
        self.exitCode                           = 0

        # Convenience vars
        self.dp                                 = pfmisc.debug(
                                                    verbosity   = self.verbosityLevel,
                                                    within      = self.__name__
                                                    )
        self.log                                = pfmisc.Message()
        self.log.syslog(True)
        self.tic_start                          = 0.0
        self.pp                                 = pprint.PrettyPrinter(indent=4)

    def __init__(self, *args, **kwargs):
        """
        DESC
            Constructor for the tsmake module -- mostly
            a thin fall through to the declare_selfvars()
            method -- the relative sparsity of this method
            is due to the object design patter that would
            have "variable assignment" code handled by
            self.declare_selfvars() and any calls to specific
            setup methods handled here.
        """

        # pudb.set_trace()
        self.declare_selfvars(*args, **kwargs)
        self.markdown   = SMarkDown()

    def env_check(self, *args, **kwargs):
        """
        DESC
            This method provides a common entry for any checks on the
            environment (input / output dirs, etc). Essentially, this
            method checks the at the <self.str_outputDir> was specified
            and that the <self.str_inputDir> exists.

        IMPLICIT INPUT
            self.str_outputDir
            self.str_inputDir

        RETURN
            {
                'status':       True|False
                'str_error':    Optional error message
            }
        """
        b_status    = True
        str_error   = ''
        if not len(self.str_outputDir):
            b_status    = False
            str_error   = 'output directory not specified.'
            self.dp.qprint(str_error, comms = 'error')
            error.fatal(self, 'outputDirFail', drawBox = True)
        if not os.path.isdir(self.str_inputDir):
            b_status    = False
            str_error   = 'input dirspec does seem to be a valid directory.'
            self.dp.qprint(str_error, comms = 'error')
            error.fatal(self, 'inputDirFail', drawBox = True)
        return {
            'status':       b_status,
            'str_error':    str_error
        }

    def htmlSnippets_read(self, *args, **kwargs):
        """
        DESC
            Read html file snippets to use to assemble into
            final `index.html`.

            The "map" to files is stored in the self.s state
            structure.

        INPUT
            directory  = <str_directory>

        RETURN
            {
                'status':       True|False,
            }

        """
        d_ret = {
            'status':           True,
            'htmlComponents':   []
        }
        str_dataPath        = '/slideMeta/htmlComponents'
        l_htmlComponents    = list(self.data.lstr_lsnode(str_dataPath))
        d_ret['htmlComponents'] = l_htmlComponents
        str_htmlDir         = self.data.cat('slideMeta/dirComponents/html')
        for el in l_htmlComponents:
            str_fileDP      = '%s/%s/file'      % (str_dataPath, el)
            str_contentsDP  = '%s/%s/contents'  % (str_dataPath, el)
            str_fileName    = self.data.cat(str_fileDP)
            str_file        = '%s/%s' % (str_htmlDir, str_fileName)
            with open(str_file, 'r') as fb:
                str_contents = fb.read()
                self.data.touch(str_contentsDP, str_contents)

        return d_ret

    def slide_filesRead(self, *args, **kwargs):
        """
        DESC
            Read a series of globbed text slide files into
            relevant internal data structures.

        INPUT
            directory  = <str_directory>

        RETURN
            {
                'status':       True|False,
                'numSlides':    <int>num
            }

        """

        b_status        = True
        str_directory   = './'


        for k, v in kwargs.items():
            if k == 'directory':        str_directory   = v

        self.lstr_slideFiles    = sorted(
                                    glob.glob(str_directory +
                                    '/' + self.str_slideListGlob)
                                )
        if len(self.lstr_slideFiles):
            for str_file in self.lstr_slideFiles:
                with open(str_file) as fp:
                    self.ld_slide.append(hjson.load(fp))

        return {
            'status':           b_status,
            'numSlides':        len(self.lstr_slideFiles)
        }

    def htmlPage_assemble(self):
        """
        DESC
            The main method for building the index.html page
            by combining the snippets and incorporating the
            hjson slides.

        INPUT

        RETURN
            d_ret   = {
                'status':       True|False
                'pageHTML':     HTMLstring
            }
        """
        b_status        = True
        str_dataPath    = '/slideMeta/htmlComponents'
        str_pageHTML    = ""

        def numberOfSlides_find():
            """
            DESC
                Simply return the number of slides.

            INPUT
                self

            OUTPUT
                Integer count of the number of slides.
            """
            return len(self.ld_slide)

        def head_assemble(astr_page):
            """
            DESC
                Create the doctype and head component, appending to
                the input <astr_page>

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """
            self.dp.qprint("Assembing head...", level = 2)
            astr_page   ='''%s%s<html>\n%s
            ''' % ( astr_page,
                    self.data.cat('%s/%s/contents' % (str_dataPath, 'doctype')),
                    self.data.cat('%s/%s/contents' % (str_dataPath, 'head')))
            return astr_page

        def body_titleAssemble(astr_page):
            """
            DESC
                Assemble the title portion of the page

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """
            self.dp.qprint("Assembing title portion...", level = 2)

            astr_page += self.data.cat('%s/title/contents' % str_dataPath)
            astr_page += "\n"
            return astr_page

        def body_logosAssemble(astr_page):
            """
            DESC
                Assemble the logos portion of the page

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """
            if not self.b_noLogos:
                self.dp.qprint("Assembing logos portion...", level = 2)

                astr_page += self.data.cat('%s/logos/contents' % str_dataPath)
                astr_page += "\n"
            return astr_page

        def body_navBarAssemble(astr_page):
            """
            DESC
                Assemble the navBar portion of the page

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """
            self.dp.qprint("Assembing nav bar...", level = 2)
            astr_page += '''\n<body>

    <div class="metaData" id="numberOfSlides" style="margin-bottom: -16px;">%s</div>
    <div class="metaData" id="slideIDprefix"  style="margin-bottom: -16px;">%s</div>

            ''' % (
                numberOfSlides_find(),
                self.str_slidePrefixDOMID
            )

            astr_page += self.data.cat('%s/navbar/contents' % str_dataPath)
            astr_page += "\n"
            return astr_page

        def body_navAndLogosAssemble(astr_page):
            """
            DESC
                Create the "initial" part of the body string.

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """
            self.dp.qprint("Assembing nav bar and logos...", level = 2)
            astr_page += '''\n<body>

    <div class="metaData" id="numberOfSlides">%s</div>
    <div class="metaData" id="slideIDprefix">%s</div>

            ''' % (
                numberOfSlides_find(),
                self.str_slidePrefixDOMID
            )

            astr_page += self.data.cat('%s/navbar/contents' % str_dataPath)
            astr_page += "\n"
            if not self.b_noLogos:
                astr_page += self.data.cat('%s/logos/contents'  % str_dataPath)
            astr_page += "\n"
            return astr_page

        def slideText_process(astr_slideText, a_slideCount):
            """
            DESC
                Perform some optional processing on slide text.

                First, parse and process any "markdown", then remove
                any ''' chars in the text and optionally pad to a
                fixed number of rows.

                In addition, any 'order-X' ids are replaced with
                'order-<slide>-X' ids.

            INPUT
                astr_slideText      text of slide

            RETURN
                astr_slideText      updated text
            """
            def rows_addToBottom(astr_slideText):
                """
                A simple method that adds some "blank" lines to
                <pre> formatted slides.

                In some ways this is deprecated since results are
                somewhat haphazard with more complex slides.
                """
                rows            = astr_slideText.count('\n')
                if self.textNumRows and rows < self.textNumRows:
                    rowsToAdd       = self.textNumRows - rows
                    str_rowsToAdd   = '\n' * rowsToAdd + '</pre>'
                    str_replaceFrom = '</pre>'
                    maxreplace      = 1
                    astr_slideText  = str_rowsToAdd.join(
                                        astr_slideText.rsplit(
                                            str_replaceFrom, maxreplace
                                        )
                                    )
                return astr_slideText

            astr_slideText  = self.markdown.run(astr_slideText)
            astr_slideText  = astr_slideText.replace("'''", '')
            astr_slideText  = astr_slideText.replace(
                                    'order',
                                    'order-%d' % a_slideCount
                                )
            astr_slideText  = astr_slideText.replace(
                                    'typewriter',
                                    'typewriter-%d' % a_slideCount
                                )
            astr_slideText  = rows_addToBottom(astr_slideText)
            return astr_slideText

        def body_slidesAssemble(astr_page):
            """
            DESC
                Embed the slides into the body.

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """

            def title_make(hjsonslide, str_DOMID):
                """
                Return the HTML for the title of the slide.
                """
                str_title =  '''\n
                <!--------------------------- %s --------------------------->
                <div id="%s-title" style="display: none;">
                    %s
                </div> <!--- title div --->\n''' % ( str_DOMID,
                                str_DOMID,
                                slide['title'])
                return str_title

            def slideStyle_determine(hjsonslide):
                """
                Simply determine the style to apply, based on
                parsing the hjson slide.

                RETURN:
                A string denoting the style to apply:

                    'default'
                    'oldStyleTerminal'

                """
                if 'body-class' in hjsonslide:
                    str_slideClass = slide['body-class']
                    if 'terminal' in str_slideClass:
                        return 'oldStyleTerminal'
                return 'default'

            def default_styleApply( hjsonslide,
                                    slideCount,
                                    str_slideStyle,
                                    str_slideClass):
                """
                Apply the default style to the slide.

                INPUT:
                The HJSON slide

                RETURN:
                The slide <div> HTML string
                """
                str_slideText   = slideText_process(hjsonslide['body'], slideCount)
                if 'body-style' in hjsonslide:
                    str_slideStyle = 'style="display:none; %s"' % slide['body-style']
                str_slideDiv    = '''
                <div class="%s" id="%s" name="%s" %s>
%s
                </div> <!--- slide div --->
                <!--------------------------- slide-%d end ----------------------->

        ''' % (     str_slideClass, str_DOMID, str_DOMID, str_slideStyle,
                    str_slideText, slideCount)
                return str_slideDiv

            def oldStyleTerminal_styleApply(hjsonslide,
                                            slideCount,
                                            str_slideStyle,
                                            str_slideClass):
                """
                Define an old-style terminal

                INPUT:
                The HJON slide

                RETURN:
                The slide <div> HTML string
                """
                str_slideText   = slideText_process(hjsonslide['body'], slideCount)
                if 'body-style' in hjsonslide:
                    str_slideStyle = 'style="display:none; %s"' % slide['body-style']
                str_slideDiv    = '''
                <section class = "terminal">

                        <div class="%s" id="%s" name="%s" %s>\n%s
                        </div>

                <div class="interlace"></div>
                <!--- <div class="CRT"></div> -->

                </section>


                <!--------------------------- end --------------------------->

        ''' % (     str_slideClass, str_DOMID, str_DOMID, str_slideStyle,
                    str_slideText)
                return str_slideDiv


            self.dp.qprint("Assembing individual slides...", level = 2)
            astr_page += '''\n    <div class="formLayout">'''
            slideCount = 1
            for slide in self.ld_slide:
                str_slide       = ""
                self.dp.qprint("\tAssembing slide %d..." % slideCount, level = 3)
                str_DOMID       = "%s%d" % (self.str_slidePrefixDOMID, slideCount)
                str_slideStyle  = 'style="display: none;"'
                str_slideClass  = "container slide "

                str_slide      += title_make(slide, str_DOMID)
                slideStyle      = slideStyle_determine(slide)
                str_slide      += eval('''%s_styleApply(slide,
                                                        slideCount,
                                                        str_slideStyle,
                                                        str_slideClass)''' % slideStyle)

                self.dp.qprint("\tslide %d:\n%s" % (slideCount, str_slide),
                                level = 4)
                slideCount += 1
                astr_page  += str_slide
            astr_page += '\n        <div class="modal"><!-- Place at bottom of page --></div>\n'
            astr_page += "    </div>"
            return astr_page

        def footer_assemble(astr_page):
            """
            DESC
                Assemble the footer.

            INPUT
                astr_page       current html code of page

            RETURN
                astr_page       updated html code of page
            """
            self.dp.qprint("Assembing footer...", level = 2)
            astr_page += "\n"
            astr_page += self.data.cat('%s/footer/contents'  % str_dataPath)
            astr_page += '''
    <script src="termynal.js" data-termynal-container="#termynal_pfdcm|#termynal_pacsQuery|#termynal_pacsRetriveStatus"></script>
    <script src="js/tslide.js"></script>
</body>
</html>'''
            return astr_page

        str_pageHTML    = footer_assemble(
                            body_slidesAssemble(
                                body_titleAssemble(
                                    body_logosAssemble(
                                        body_navBarAssemble(
                                            head_assemble(str_pageHTML)
                                        )
                                    )
                                )
                            )
                        )
        return {
            'status':       b_status,
            'pageHTML':     str_pageHTML
        }

    def slide_masterRead(self) -> dict:
        """
        Read the master slide file and return a complete dictionary
        representation.

        Returns:
            dict: parsed representation of the master slide
        """
        d_ret   = {
            'status':           False,
            'slideFileList':    [],
            'numSlides':        0,
            'msg':              "No input slidesFile processed"
        }
        str_fileContents:str    = ""
        if len(self.str_slidesFile):
            try:
                fp: io.TextIOWrapper    = open("%s/%s" %
                                            (self.str_inputDir,
                                             self.str_slidesFile), "r")
                d_ret['status']         = True
                str_fileContents        = fp.read()
                d_ret['slideFileList']  = str_fileContents.\
                                            split(self.str_slidesFileBreak)
                d_ret['numSlides']      = len(d_ret['slideFileList'])
                self.ld_slide:list      = [hjson.loads(x) for x in d_ret['slideFileList']]
                fp.close()
            except:
                d_ret['status']         = False
                d_ret['msg']            = 'File %s/%s not accessible' % \
                                            (self.str_inputDir,
                                             self.str_slidesFile)
        return d_ret

    def slidesFile_break(self):
        """
        DESC
            Separate a single input text file into constituent
            individual slide files, breaking on a given
            break token.

            Resultant files are stored in the <inputDir>, using
            <slidePrefixDOMID>-<indexCount>.

        INPUT
            astr_slideFileName      name of input file to split

        RETURN
            d_ret {
                'status':           True|False,
                'numSlides':        numberOfSlideFiles,
                'slideFileList:'    listOfSlideFilesCreated,
                'msg':              ""
            }
        """
        d_ret = {
            'status':           False,
            'numSlides':        0,
            'slideFileList':    [],
            'msg':              "No input slidesFile processed"
        }

        d_ret   = self.slide_masterRead()

        # if len(self.str_slidesFile):
        #     try:
        #         fp              = open("%s/%s" %
        #                                 (self.str_inputDir,
        #                                  self.str_slidesFile), "r")
        #         str_contents    = fp.read()
        #         d_ret['status'] = True
        #         fp.close()
        #     except:
        #         d_ret['status'] = False
        #         d_ret['msg']    = 'File %s/%s not accessible' % \
        #                                 (self.str_inputDir,
        #                                  self.str_slidesFile)

        if d_ret['status']:
            # d_ret['slideFileList']   = str_contents.split(self.str_slidesFileBreak)
            slideCount:int      = 0
            for slide in d_ret['slideFileList']:
                slideCount += 1
                with open('%s/%s%03d.hjson' % (self.str_inputDir,
                                            self.str_slidePrefixDOMID,
                                            slideCount), 'w') as fp:
                    fp.write(slide)
            d_ret['msg']        = 'Slides created successfully'
            d_ret['numSlides']  = slideCount
        return d_ret

    def filelist_prune(self, at_data, *args, **kwargs):
        """
        DESC
            Given a list of files, possibly prune list by
            extension.

        NOTE:
            This is a historical method and not currently
            used! It is conserved for now in case a `pfree`
            directory walk is used in future.

            The somewhat cumbersome calling signature is
            due to `pfree` callback requirements.
        """

        b_status    = True
        l_file      = []
        str_path    = at_data[0]
        al_file     = at_data[1]
        if len(self.str_extension):
            al_file = [x for x in al_file if self.str_extension in x]

        if len(al_file):
            al_file.sort()
            l_file      = al_file
            b_status    = True
        else:
            self.dp.qprint( "No valid files to analyze found in path %s!" % str_path,
                            comms = 'error', level = 3)
            l_file      = None
            b_status    = False
        return {
            'status':   b_status,
            'l_file':   l_file
        }

    def ret_dump(self, d_ret, **kwargs):
        """
        DESC
            JSON print results to console (or caller) pending
            state of passed kwargs.
        """
        b_print     = True
        for k, v in kwargs.items():
            if k == 'JSONprint':    b_print     = bool(v)
        if b_print:
            print(
                json.dumps(
                    d_ret,
                    indent      = 4,
                    sort_keys   = True
                )
        )

    def run(self, *args, **kwargs):
        """
        DESC
            The run method is the main entry point to the operational
            behaviour of the script.

        INPUT
            [timerStart      = True|False]

        RETURN
        {
            'status':       True|False
        }
        """

        b_status            = True
        d_env               = self.env_check()
        b_timerStart        = False
        d_inputFile:dict         = {}
        d_slides            = {}
        d_html              = {}
        d_assemble          = {}
        d_ret               = {}
        numSlides           = 0

        self.dp.qprint(
                "Starting tsmake run... ",
                level = 1
                )

        for k, v in kwargs.items():
            if k == 'timerStart':   b_timerStart    = bool(v)

        if b_timerStart:
            other.tic()

        if not self.b_noPageSplit:
            # Process an optional input file to split into slides
            d_inputFile     = self.slidesFile_break()
        else:
            d_inputFile     = self.slide_masterRead()

        if d_inputFile['status']:
            # read input slides
            d_slides        = self.slide_filesRead(directory = self.str_inputDir)
            numSlides       = d_slides['numSlides']
            # read html components
            if d_slides['status']:
                d_html          = self.htmlSnippets_read()

                # assemble the HTML page
                if d_html['status']:
                    d_assemble      = self.htmlPage_assemble()

                    # now create the output dir
                    other.mkdir(self.str_outputDir)

                    # write the index.html file
                    with open('%s/index.html' % self.str_outputDir, "w") as fp:
                        fp.write(d_assemble['pageHTML'])

                    # and copy necessary dirs
                    l_supportDirs   = ['./css', './fortunes', './images', './js', './logos']
                    l_userDirs      = []
                    if len(self.str_additionalDirList):
                        l_userDirs  = self.str_additionalDirList.split(',')
                    for str_dir in l_supportDirs + l_userDirs:
                        self.dp.qprint("Copying dir %s... to %s/%s" % \
                            (
                                str_dir,
                                self.str_outputDir,
                                os.path.basename(str_dir)
                            ),
                            level = 2)
                        copy_tree('%s' % str_dir, '%s/%s' %
                                                (self.str_outputDir,
                                                os.path.basename(str_dir)))


        d_ret = {
            'status':           b_status,
            'd_env':            d_env,
            'd_inputFile':      d_inputFile,
            'd_slides':         d_slides,
            'd_html':           d_html,
            'd_assemble':       d_assemble,
            'numSlides':        numSlides,
            'runTime':          other.toc()
        }

        self.dp.qprint('Returning from tslide run...', level = 1)
        return d_ret
