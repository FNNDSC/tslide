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

from        distutils.dir_util  import  copy_tree

# Imports for the "fortune" auto-generating
import      fortune
import      cowsay
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
        self.args                       = kwargs
        self.__name__                   = "tsmake"

        # Parse CLI args
        for key, value in kwargs.items():
            if key == 'inputDir':           self.str_inputDir           = value
            if key == "outputDir":          outputDir_process(value) 
            if key == 'verbosity':          self.verbosityLevel         = int(value)
            if key == 'json':               self.b_json                 = bool(value)
            if key == 'followLinks':        self.b_followLinks          = bool(value)
            if key == 'fortune':            self.fortuneSlides          = int(value)
            if key == 'slidePrefixDOMID':   self.str_slidePrefixDOMID   = value
            if key == 'slideListGlob':      self.str_slideListGlob      = value
            if key == 'slideTextNumRows':   self.textNumRows            = int(value)
            if key == 'slidesFile':         self.str_slidesFile         = value
            if key == 'slidesFileBreak':    self.str_slidesFileBreak    = value

        # Slide lists and dictionaries
        self.lstr_slideFiles            = []
        self.ld_slide                   = []
        self.str_extension              = "hjson"

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
        self.pf_tree                    = None
        self.numThreads                 = 1

        # Some output handling
        self.str_stdout                 = ''
        self.str_stderr                 = ''
        self.exitCode                   = 0

        # Convenience vars
        self.b_json                     = False
        self.dp                         = pfmisc.debug(    
                                            verbosity   = self.verbosityLevel,
                                            within      = self.__name__
                                            )
        self.log                        = pfmisc.Message()
        self.log.syslog(True)
        self.tic_start                  = 0.0
        self.pp                         = pprint.PrettyPrinter(indent=4)

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
            astr_page += self.data.cat('%s/logos/contents'  % str_dataPath)
            astr_page += "\n"
            return astr_page

        def slideText_process(astr_slideText):
            """
            DESC
                Perform some optional processing on slide text.

                This essentially means removing the ''' chars and
                optionally padding to fixed number of rows.

            INPUT
                astr_slideText      text of slide

            RETURN
                astr_slideText      updated text
            """
            astr_slideText  = astr_slideText.replace("'''", '')            
            rows            = astr_slideText.count('\n')
            if rows < self.textNumRows:
                rowsToAdd       = self.textNumRows - rows
                str_rowsToAdd   = '\n' * rowsToAdd + '</pre>'
                str_replaceFrom = '</pre>'
                maxreplace      = 1
                astr_slideText  = str_rowsToAdd.join(astr_slideText.rsplit(str_replaceFrom, maxreplace))
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
            self.dp.qprint("Assembing individual slides...", level = 2)
            astr_page += '''\n    <div class="formLayout">'''

            slideCount = 1
            for slide in self.ld_slide:
                self.dp.qprint("\tAssembing slide %d..." % slideCount, level = 3)
                str_DOMID  = "%s%d" % (self.str_slidePrefixDOMID, slideCount)
                astr_page += '''\n
        <div id="%s-title" style="display: none;">
            %s
        </div>\n''' % ( str_DOMID, 
                        slide['title'])
                str_slideText   = slideText_process(slide['body'])
                self.dp.qprint("\tslide %d:\n%s" % (slideCount, str_slideText), 
                                level = 4)
                astr_page += '''
        <div class="container" id="%s" name="%s" style="display: none;">
%s
        </div>''' % (str_DOMID, str_DOMID, str_slideText)
                slideCount += 1
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
                                body_navAndLogosAssemble(
                                    head_assemble(str_pageHTML)
                                )
                            )
                        )
        return {
            'status':       b_status,
            'pageHTML':     str_pageHTML
        }
                

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

        if len(self.str_slidesFile):
            try:
                fp              = open(self.str_slidesFile, "r")
                str_contents    = fp.read()
                d_ret['status'] = True
                fp.close()
            except:
                d_ret['status'] = False
                d_ret['msg']    = 'File %s/%s not accessible' % \
                                        (self.str_inputDir,
                                         self.str_slidesFile)
            
            if d_ret['status']:
                d_ret['slideFileList']   = str_contents.split(self.str_slidesFileBreak)
                slideCount      = 0
                for slide in d_ret['slideFileList']:
                    slideCount += 1
                    with open('%s/%s%d.hjson' % (self.str_inputDir, 
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
        d_inputFile         = {}
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

        # Process an optional input file to split into slides
        d_inputFile     = self.slidesFile_break()

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
                    l_supportDirs   = ['css', 'fortunes', 'images', 'js', 'logos']
                    for str_dir in l_supportDirs:
                        self.dp.qprint("Copying dir %s..." % str_dir, level = 2)
                        copy_tree('./%s' % str_dir, '%s/%s' % 
                                                (self.str_outputDir, 
                                                str_dir))

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

        if self.b_json:
            self.ret_dump(d_ret, **kwargs)

        self.dp.qprint('Returning from tslide run...', level = 1)
        return d_ret
        