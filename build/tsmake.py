# System imports
import      os
import      getpass
import      argparse
import      json
import      pprint
import      re
import      logging

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

class D(S):
    """
    A derived 'pfstate' class that keeps system state.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """

        for k,v in kwargs.items():
            if k == 'args':     d_args          = v

        S.__init__(self, *args, **kwargs)
        if not S.b_init:
            d_specific  = \
                {
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
                        'head':     {},
                        'navbar':   {},
                        'logos':    {},
                        'body':     {},
                        'footer':   {}
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
            'exitCode'      : 1}
        }


    def declare_selfvars(self):
        """
        A block to declare self variables
        """

        #
        # Object desc block
        #
        self.str_desc                   = ''
        self.__name__                   = "tsmake"
        self.str_version                = '0.99'

        # Directory and filenames
        self.str_inputDir               = ''
        self.str_inputFile              = ''
        self.str_extension              = ''
        self.str_outputFileStem         = ''
        self.str_ouptutDir              = ''

        # state
        self.s                          = D(*args, **kwargs)

        # pftree dictionary
        self.pf_tree                    = None
        self.numThreads                 = 1

        self.str_stdout                 = ''
        self.str_stderr                 = ''
        self.exitCode                   = 0

        self.b_json                     = False

        # Convenience vars
        self.dp                         = None
        self.log                        = None
        self.tic_start                  = 0.0
        self.pp                         = pprint.PrettyPrinter(indent=4)
        self.verbosityLevel             = 1

    def __init__(self, *args, **kwargs):
        """
        Constructor for the tsmake module.
        """

        def outputDir_process(str_outputDir):
            if str_outputDir == '%inputDir':
                self.str_outputDir  = self.str_inputDir
            else:
                self.str_outputDir  = str_outputDir

        # pudb.set_trace()
        self.declare_selfvars(self)

        for key, value in kwargs.items():
            if key == 'inputDir':           self.str_inputDir           = value
            if key == 'maxDepth':           self.maxDepth               = int(value)
            if key == 'inputFile':          self.str_inputFile          = value
            if key == "outputDir":          outputDir_process(value) 
            if key == 'outputFileStem':     self.str_outputFileStem     = value
            if key == 'outputLeafDir':      self.str_outputLeafDir      = value
            if key == 'extension':          self.str_extension          = value
            if key == 'threads':            self.numThreads             = int(value)
            if key == 'extension':          self.str_extension          = value
            if key == 'verbosity':          self.verbosityLevel         = int(value)
            if key == 'json':               self.b_json                 = bool(value)
            if key == 'followLinks':        self.b_followLinks          = bool(value)

        # Declare pf_tree
        self.pf_tree    = pftree.pftree(
                            inputDir                = self.str_inputDir,
                            maxDepth                = self.maxDepth,
                            inputFile               = self.str_inputFile,
                            outputDir               = self.str_outputDir,
                            outputLeafDir           = self.str_outputLeafDir,
                            threads                 = self.numThreads,
                            verbosity               = self.verbosityLevel,
                            followLinks             = self.b_followLinks,
                            relativeDir             = True
        )

        # Set logging
        self.dp                        = pfmisc.debug(    
                                            verbosity   = self.verbosityLevel,
                                            within      = self.__name__
                                            )
        self.log                       = pfmisc.Message()
        self.log.syslog(True)

    def env_check(self, *args, **kwargs):
        """
        This method provides a common entry for any checks on the 
        environment (input / output dirs, etc)
        """
        b_status    = True
        str_error   = ''
        if not len(self.str_outputDir): 
            b_status = False
            str_error   = 'output directory not specified.'
            self.dp.qprint(str_error, comms = 'error')
            error.warn(self, 'outputDirFail', drawBox = True)
        return {
            'status':       b_status,
            'str_error':    str_error
        }


    def slide_fileRead(self, *args, **kwargs):
        """
        Read a DICOM file and perform some initial
        parsing of tags.

        NB!
        For thread safety, class member variables
        should not be assigned since other threads
        might override/change these variables in mid-
        flight!
        """

        def dcmToStr_doExplicit(d_dcm):
            """
            Perform an explicit element by element conversion on dictionary
            of dcm FileDataset
            """
            b_status = True
            self.dp.qprint('In directory: %s' % os.getcwd(),     comms = 'error')
            self.dp.qprint('Failed to str convert %s' % str_file,comms = 'error')
            self.dp.qprint('Possible source corruption or non standard tag',
                            comms = 'error')
            self.dp.qprint('Attempting explicit string conversion...',
                            comms = 'error')
            l_k         = list(d_dcm.keys())
            str_raw     = ''
            str_err     = ''
            for k in l_k:
                try:
                    str_raw += str(d_dcm[k])
                    str_raw += '\n'
                except:
                    str_err = 'Failed to string convert key "%s"' % k
                    str_raw += str_err + "\n"
                    self.dp.qprint(str_err, comms = 'error')
                    b_status = False
            return str_raw, b_status

        b_status        = False
        l_tags          = []
        l_tagsToUse     = []
        d_tagsInString  = {}
        str_file        = ""
        str_outputFile  = ""

        d_DICOM           = {
            'dcm':              None,
            'd_dcm':            {},
            'strRaw':           '',
            'l_tagRaw':         [],
            'd_json':           {},
            'd_dicom':          {},
            'd_dicomSimple':    {}
        }

        for k, v in kwargs.items():
            if k == 'file':             str_file    = v
            if k == 'l_tagsToUse':      l_tags      = v

        if len(args):
            l_file          = args[0]
            str_file        = l_file[0]

        str_localFile   = os.path.basename(str_file)
        str_path        = os.path.dirname(str_file)
        # self.dp.qprint("%s: In input base directory:      %s" % (threading.currentThread().getName(), self.str_inputDir))
        # self.dp.qprint("%s: Reading DICOM file in path:   %s" % (threading.currentThread().getName(),str_path))
        # self.dp.qprint("%s: Analysing tags on DICOM file: %s" % (threading.currentThread().getName(),str_localFile))      
        # self.dp.qprint("%s: Loading:                      %s" % (threading.currentThread().getName(),str_file))

        try:
            d_DICOM['dcm']  = dicom.read_file(str_file)
            b_status        = True
        except:
            self.dp.qprint('In directory: %s' % os.getcwd(),    comms = 'error')
            self.dp.qprint('Failed to read %s' % str_file,      comms = 'error')
            b_status        = False
        if b_status:
            d_DICOM['l_tagRaw'] = d_DICOM['dcm'].dir()
            d_DICOM['d_dcm']    = dict(d_DICOM['dcm'])
            try:
                d_DICOM['strRaw']   = str(d_DICOM['dcm'])
            except:
                d_DICOM['strRaw'], b_status = dcmToStr_doExplicit(d_DICOM['d_dcm'])

            if len(l_tags):
                l_tagsToUse     = l_tags
            else:
                l_tagsToUse     = d_DICOM['l_tagRaw']

            if 'PixelData' in l_tagsToUse:
                l_tagsToUse.remove('PixelData')

            for key in l_tagsToUse:
                d_DICOM['d_dicom'][key]       = d_DICOM['dcm'].data_element(key)
                try:
                    d_DICOM['d_dicomSimple'][key] = getattr(d_DICOM['dcm'], key)
                except:
                    d_DICOM['d_dicomSimple'][key] = "no attribute"
                d_DICOM['d_json'][key]        = str(d_DICOM['d_dicomSimple'][key])

            # pudb.set_trace()
            d_tagsInString  = self.tagsInString_process(d_DICOM, self.str_outputFileStem)
            str_outputFile  = d_tagsInString['str_result']

        return {
            'status':           b_status,
            'inputPath':        str_path,
            'inputFilename':    str_localFile,
            'outputFileStem':   str_outputFile,
            'd_DICOM':          d_DICOM,
            'l_tagsToUse':      l_tagsToUse
        }

    def filelist_prune(self, at_data, *args, **kwargs):
        """
        Given a list of files, possibly prune list by 
        extension.
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
        JSON print results to console (or caller)
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
        The run method is the main entry point to the operational 
        behaviour of the script.
        """

        b_status            = True
        d_pftreeRun         = {}
        d_inputAnalysis     = {}
        d_env               = self.env_check()
        b_timerStart        = False

        self.dp.qprint(
                "\tStarting pfdicom run... (please be patient while running)", 
                level = 1
                )

        for k, v in kwargs.items():
            if k == 'timerStart':   b_timerStart    = bool(v)

        if b_timerStart:
            other.tic()

        if d_env['status']:
            d_pftreeRun = self.pf_tree.run(timerStart = False)
        else:
            b_status    = False 

        str_startDir    = os.getcwd()
        os.chdir(self.str_inputDir)
        if b_status:
            if len(self.str_extension):
                d_inputAnalysis = self.pf_tree.tree_process(
                                inputReadCallback       = None,
                                analysisCallback        = self.filelist_prune,
                                outputWriteCallback     = None,
                                applyResultsTo          = 'inputTree',
                                applyKey                = 'l_file',
                                persistAnalysisResults  = True
                )
        os.chdir(str_startDir)

        d_ret = {
            'status':           b_status and d_pftreeRun['status'],
            'd_env':            d_env,
            'd_pftreeRun':      d_pftreeRun,
            'd_inputAnalysis':  d_inputAnalysis,
            'runTime':          other.toc()
        }

        if self.b_json:
            self.ret_dump(d_ret, **kwargs)

        self.dp.qprint('\tReturning from pfdicom run...', level = 1)

        return d_ret
        