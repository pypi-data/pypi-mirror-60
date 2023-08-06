# -*- coding: utf-8 -*-
from __future__ import print_function
import os, copy, math

# external libraries imports
import numpy as np

try:
    from scipy.optimize import nnls
except:
    nnls = None
# softgrid imports
try:
    from softgrid import Orchestrator
    from softgrid import Globals as softgridGlobals
except:
    Orchestrator = None

# fullrmc imports
from .Globals import FLOAT_TYPE, basestring, LOGGER, xrange



class WorkersManagement(object):
    """Used by remote `softgrid <https://bachiraoun.github.io/softgrid/index.html>`_ worker
    to run fullrmc stochastic engine

    .. code-block:: python

         from fullrmc.Engine import Engine
         from fullrmc import MultiframeUtils

         # create engine
         ENGINE = Engine().load(path)

         # run on grid
         WM = MultiframeUtils.WorkersManagement()
         WM.start(engine=ENGINE, multiframe='size_distribution', orchestrator=None)

         # run independant.
         WM.run_independant(self, nCycle=10, numberOfSteps=1000, saveFrequency=1)

         # run dependant
         WM.run_dependant(nCycle=200, firstNAccepted=1, subframesWeight=None, numberOfSteps=100, saveFrequency=10)



    """
    def __init__(self, repoTimeout=10, requestTimeout=60):
        if Orchestrator is None:
            print("Unable to import softgrid. Launching fullrmc stochastic engine remotely is not possible")
            return
        self._orchestrator   = None
        self._requestTimeout = requestTimeout
        self._repoTimeout    = repoTimeout
        self._allowedModes   = None
        self.__requesting    = False


    def start(self, engine, multiframe, orchestrator=None, workerRequestLoopTimeout=3600):
        self.__requesting  = False
        # set parameters
        self._engine     = engine
        self._multiframe = multiframe
        # check multiframe
        isNormalFrame, isMultiframe, isSubframe = self._engine.get_frame_category(self._multiframe)
        assert isMultiframe, "At user fullrmc frame must be a multiframe, '%s' is given instead"%(self._multiframe)
        # get subframes and jobs password
        self._subframes = [os.path.join(self._multiframe, fn) for fn in self._engine.frames[self._multiframe]['frames_name']]
        self._passwords = self._subframes
        ## set used frame as first subframe just to make sure multiframe subframes are created
        self._engine.set_used_frame(frame=self._subframes[0], _updateRepo=False)
        ## create orchestrator
        self._orchestrator = orchestrator
        if self._orchestrator is None:
            softgridGlobals.RULES['machine_maximum_number_of_workers'] = None
            logKwargs = {'logTypes':{'execution_started': {'stdoutFlag':False, 'fileFlag':False},
                                     'execution_finished':{'stdoutFlag':False, 'fileFlag':False},
                                     'result':            {'stdoutFlag':False, 'fileFlag':False},
                                    }
                        }
            self._orchestrator = Orchestrator(password='nopassword', acceptWorkers=True, logKwargs=logKwargs)
        assert isinstance(self._orchestrator, Orchestrator),"orchestrator must be a softgrid.Orchestrator instance. %s is given instead"%(orchestrator)
        # check and create workers
        if len(self._orchestrator.workers)<len(self._subframes):
            status, ss,fl = self._orchestrator.launch_worker(upgridUniqueName=self._orchestrator.gridUniqueName,
                                            executorKwargs={'logKwargs':logKwargs},
                                            executorAddress=[self._orchestrator.address]*(len(self._subframes)-len(self._orchestrator.workers)),
                                            machineUser=['some_user']*(len(self._subframes)-len(self._orchestrator.workers)))
        assert len(self._orchestrator.workers)>=len(self._subframes), "Not enough workers launched. Needing %i while %i were successfully launched"%(len(self._subframes),len(self._orchestrator.workers))
        ## set worker to password lut
        workers       = self._orchestrator.workers
        self._workers = [workers[idx] for idx in range(len(self._subframes))]
        self._workerPasswordLUT = dict([(w,p) for w,p in zip(self._workers,self._passwords)])
        self._workerPasswordLUT.update( dict([(p,w) for w,p in zip(self._workers,self._passwords)]) )
        assert len(self._workerPasswordLUT)==2*len(self._passwords), "redundancy in workers and passwords name. PLEASE REPORT"
        ## release all previous requests from tracking. Old errors might be still there from last run
        self._release_all_requests()
        ## launch workers request loop
        code = """
def launch_fullrmc_worker(executor, repoTimeout, requestTimeout, userGun, password, engineFilePath, frame, requestLoopTimeout):
    from fullrmc import MultiframeUtils
    from importlib import reload
    reload(MultiframeUtils)
    WM = MultiframeUtils.WorkersManagement(repoTimeout=repoTimeout,
                                          requestTimeout=requestTimeout)
    WM._on_worker(executor=executor,
                  userGun=userGun,
                  password=password,
                  engineFilePath=engineFilePath,
                  frame=frame,
                  requestLoopTimeout=requestLoopTimeout)
    """
        # get transferKwargs
        TK = self._orchestrator.get_transfer_template(priority=None, func={'launch_fullrmc_worker':code})
        TK['first_argument_executor'] = True
        TK['kwargs']   = {"repoTimeout":self._repoTimeout,
                          "requestTimeout":self._requestTimeout,
                          "userGun":self._orchestrator.gridUniqueName,
                          "engineFilePath":self._engine.path,
                          "requestLoopTimeout":workerRequestLoopTimeout}
        # loop transfers
        transferKwargs = [copy.deepcopy(TK) for _ in self._passwords]
        _ = [tk['kwargs'].setdefault('frame', frm) for tk,frm in zip(transferKwargs, self._subframes)]
        _ = [tk['kwargs'].setdefault('password', pwd) for tk,pwd in zip(transferKwargs, self._passwords)]
        ## wait for workers to request engine MODE given experimental constraints
        try:
            self._orchestrator.transfer(transferKwargs=transferKwargs,
                                        receivers=self._workers,
                                        collect= False)
            ## wait for request from workers
            request = self._orchestrator.wait_for_request(password=self._passwords, timeout=self._requestTimeout, frequency=0.0005)
            for pwd in self._passwords:
                if request[pwd] is None:
                    raise Exception("Timeout exhausted before request '%s' from '%s' is recieved"%(pwd, self._workerPasswordLUT[pwd]))
                elif isinstance(request[pwd]['request'], basestring):
                    if request[pwd]['request'].startswith('ERROR'):
                        raise Exception("Error for '%s' from '%s' is recieved"%(pwd, self._workerPasswordLUT[pwd]))
                    else:
                        raise Exception("Recieved un-recoginzed request '%s' from '%s'"%(pwd, self._workerPasswordLUT[pwd]))
                else:
                    assert isinstance(request[pwd]['request'], dict), "Was expecting dictionary for request '%s', received '%s' from '%s'"%(pwd,request[pwd]['request'],self._workerPasswordLUT[pwd])
                    assert 'EXPERIMENTAL_CONSTRAINT_INFO' in request[pwd]['request'], "Was expecting 'EXPERIMENTAL_CONSTRAINT_INFO' dictionary key for request '%s', received '%s' from '%s'"%(pwd,request[pwd]['request'],self._workerPasswordLUT[pwd])
        except Exception as err:
            self._release_all_requests()
            raise Exception(err)
        ## parse experimental info and respond with execution modes
        try:
            expConstData = {}
            self._allowedModes = ['RUN_ALL']
            if all([request[pwd]['request']['EXPERIMENTAL_CONSTRAINT_INFO'].pop('scipy_nnls_available') for pwd in self._passwords]):
                expInfo = {}
                for pwd in self._passwords:
                    cinfo  = request[pwd]['request']['EXPERIMENTAL_CONSTRAINT_INFO']
                    for cname in cinfo:
                        dinfo = cinfo[cname]
                        expConstData[cname] = dinfo.pop('_expData')
                        for dname in list(dinfo):
                            key = '%s-%s'%(cname,dname)
                            l = expInfo.setdefault(key,[])
                            l.append(dinfo[dname])
                if all([len(expInfo[k])==len(self._passwords) for k in expInfo]):
                    if all([len(set(expInfo[k]))==1 for k in expInfo]):
                        self._allowedModes.append('FIRST_ACCEPTED')
                        self._allowedModes.append('MULTIFRAME_PRIOR')
            # create experimental data vector
            self._experimentalVector = []
            _ = [self._experimentalVector.extend(list(expConstData[cname])) for cname in sorted(expConstData)]
            self._experimentalVector = np.array(self._experimentalVector, dtype=FLOAT_TYPE)
            self._experimentalCNames = sorted(expConstData)
            # send response
            self._orchestrator.transfer_response_to_requester(requester=self._workers,
                                                              password=self._passwords,
                                                              response=[self._allowedModes for _ in self._passwords],
                                                              errorRaise=True,
                                                              errorLog=True)
        except Exception as err:
            self._release_all_requests()
            raise Exception(err)
        # set requesting flag
        self.__requesting = True

    def stop(self):
        """ Stop WorkersManagement by disconnecting softgrid computation
        """
        if self._orchestrator is not None:
            self._orchestrator.disconnect()


    def _release_all_requests(self, onUser=True, onWorkers=True):
        gun = []
        pwd = []
        if onWorkers:
            gun.extend(self._workers)
            pwd.extend(self._passwords)
        if onUser:
            gun.extend( [self._orchestrator.gridUniqueName]*len(self._workers) )
            pwd.extend(self._passwords)
        if len(gun):
            s = self._orchestrator.transfer_release_request(gun=gun, password=pwd)

    def run_dependant(self, nCycle=100, firstNAccepted=1, numberOfSteps=100,
                            subframesWeight=10, normalize=1, driftTolerance=1,
                            saveFrequency=10, cycleTimeout=900):
        """Run all remote subframes as whole dependant structure. Subframes
        weighted (subframesWeight) atomic configuration will be used to compute
        stochastic engine's total standard error. Subframes constraints will
        also be using subframesWeight and prior to compute constraints
        standard error.
        This computation is valid under the assumption that all subframes
        might exist in the measured and modeled atomic system but they are
        far enough from each other to neglect any cross structural interactions
        and correlation


        :Parameters:
           #. nCycle (int): number of stochastic engine cycles
           #. firstNAccepted (int): number of accepted moves on subframes
              before returning result
           #. numberOfSteps (int): maximum number of steps per cycle
           #. subframesWeight (None, boolean, integer, list): Weights of
              subframes constributing to experimental constraints. If None,
              subframes weight will be fixed to normalize/numberOfSubframes if
              normalize is not None or 1./numberOfSubframes.
              If False, weights will be used as is. If True, weights will be
              updated after each cycle using non negative least square with the
              added condition of all weights must sum to 1. If integer, it's
              the frequency of updating the weights in number of cycles. If
              list, it's the fixed user defined weights to every and each
              subframe, Subframes prior are always computed after every and
              each cycle. In updated weights happen to be all 0 or only
              one subframe weight is not 0, weights will be automatically
              rescaled to  normalize/numberOfSubframes or 1./numberOfSubframes.
           #. normalize (None, number): used to normalize subframesWeight
              whether those are given or computed. Normalization will linearly
              adjust subframesWeight to ensure sum(subframesWeight) = normalize
              If None, no normalization will be done. If number it must be a
              positive non zero number. A logical value to normalize is 1 which
              minimizes the interaction between constraints scaleFactor and
              subframesWeight value
           #. driftTolerance (integer): To avoid updated subframesWeight
              drift and divergence. weights are checked for any sudden jump
              jump (increase) or drop (decrease) that doubles or split by half
              previous cycle frame weight. In case drift occurs, previous cycle
              subframesWeight are used. Tolerance defines the number of
              successive cycles weight drifts before stopping the execution.
           #. saveFrequency (int): frequency of saving all frames in between
              cycles
           #. cycleTimeout (None, integer): Estimated time for stochastic
              engine to perform 1 cycle for all frames on remote workers.
              Timeout error will be raise if cycleTimeout is exhausted before
              all workers finish the cycle work.
        """
        assert self.__requesting, "Not ready to request remote workers"
        assert isinstance(saveFrequency, int), 'saveFrequency must be int'
        # check drift tolerance
        assert isinstance(driftTolerance, int), 'driftTolerance must be int'
        assert driftTolerance>=0, "driftTolerance must be >=0"
        # check normalize
        if normalize is not None:
            assert isinstance(normalize, (int, float)), "normalize must be None or a number"
            assert normalize>0, "normalize must be >0"
            normalize = FLOAT_TYPE(normalize)
        # check subframes
        if subframesWeight is not None:
            if isinstance(subframesWeight, bool):
                if subframesWeight is True:
                    subframesWeight = 1
                else:
                    subframesWeight = 0
            elif isinstance(subframesWeight, (list,tuple,np.ndarray)):
                assert len(subframesWeight)==len(self._subframes), "subframesWeight list lengh must be equal to the number of subframes (%i)"%(len(self._subframes),)
                assert all([isinstance(w,(float,int)) for w in subframesWeight]), "list subframesWeight items must be all numbers"
                assert all([w>=0 for w in subframesWeight]), "list subframesWeight items must be all >=0"
                assert sum(subframesWeight)>0, "list subframesWeight sum must be >0"
                subframesWeight = np.array(subframesWeight, dtype=FLOAT_TYPE)
                if normalize is not None:
                    subframesWeight *= FLOAT_TYPE(normalize/np.sum(subframesWeight))
            else:
                assert isinstance(subframesWeight, int), "subframesWeight must be None, boolean, integer or a list"
                assert subframesWeight>=0, "integer subframesWeight must be >=0"
        assert numberOfSteps>0, 'numberOfSteps must be >0'
        assert isinstance(firstNAccepted, int), "firstNAccepted must be integer"
        assert firstNAccepted>0, 'firstNAccepted must be >0'
        assert firstNAccepted<numberOfSteps, 'firstNAccepted must be < numberOfSteps'
        assert isinstance(saveFrequency, int), 'saveFrequency must be int'
        assert saveFrequency>=0, "saveFrequency must be >=0"
        assert isinstance(nCycle, int), 'nCycle must be int'
        assert nCycle>0, "nCycle must be >0"
        assert isinstance(cycleTimeout, (int, float)), 'cycleTimeout must be a number'
        assert cycleTimeout>=60, "cycleTimeout must be >=60"
        # release all old requests
        self._release_all_requests(onWorkers=False)
        # build request
        _lastCycleWeigths = None
        _driftTolerance   = driftTolerance
        for step in range(nCycle):
            LOGGER.info("@%s run_dependant cycle %i/%i"%(self._multiframe, step+1,nCycle))
            _saved = False
            runRequest = [{'MODE':'FIRST_ACCEPTED', 'firstNAccepted':firstNAccepted, 'numberOfSteps':numberOfSteps}]*len(self._workers)
            self._orchestrator.transfer_request_to_responder(responder=self._workers,
                                                             password=self._passwords,
                                                             request=runRequest,
                                                             register=True,
                                                             timeout=cycleTimeout)
            responses = self._orchestrator.wait_for_response(password=self._passwords, timeout=cycleTimeout)
            # get remote experimental constraints totals
            # MUST DO THIS CACULATION ON EACH REMOTE WORKER
            # MUST CONCATENATE ALL EXPERIMENTAL CONSTRAINTS FIRST
            assert all([responses[pwd]['response']['value'] is not None for pwd in self._passwords]), "Timeout retrieving response from executors saving"
            responseVal = {}
            constNames  = None
            for pwd in responses:
                constVals = responses[pwd]['response']['value']
                if constNames is None:
                    constNames = sorted(constVals)
                assert len(set(constNames).intersection(list(constVals))) == len(constNames)
                responseVal[pwd] = constVals
            framesVector = []
            framesCoeff  = None
            for idx, CN in enumerate(self._experimentalCNames):
                framesVector.append( np.column_stack([responseVal[pwd][CN]['total'] for pwd in self._passwords]) )
                if framesCoeff is None:
                    framesCoeff = [responseVal[pwd][CN]['weight'] for pwd in self._passwords]
                else:
                    _c = [responseVal[pwd][CN]['weight'] for pwd in self._passwords]
                    assert all([i==ii for i, ii in zip(framesCoeff,_c)]), LOGGER.error("@%s subframes weight must be the same for all experimental constraints"%(self._multiframe,))
            ## compute subframes weight
            if isinstance(subframesWeight, np.ndarray):
                weights = subframesWeight
            elif subframesWeight is None:
                _n = normalize if normalize is not None else 1.
                weights = np.array([_n/len(framesCoeff) for _ in framesCoeff], dtype=FLOAT_TYPE)
                LOGGER.info("@%s subframes weight are set and fixed through all cycles to '%s'"%(self._multiframe,_n/len(framesCoeff)))
                subframesWeight = weights
            elif subframesWeight==0:
                if framesCoeff[0] is None:
                    _n = normalize if normalize is not None else 1.
                    assert all([i is None for i in framesCoeff]), LOGGER.error("@%s either all or none of subframes weight must be None"%(self._multiframe,))
                    weights = np.array([_n/len(framesCoeff) for _ in framesCoeff], dtype=FLOAT_TYPE)
                    LOGGER.info("@%s subframes weight are set and fixed through all cycles  to '%s'"%(self._multiframe,_n/len(framesCoeff)))
                else:
                    assert all([i is not None for i in framesCoeff]), LOGGER.error("@%s either all or none of subframes weight must be None"%(self._multiframe,))
                    weights = np.array(framesCoeff, dtype=FLOAT_TYPE)
                    LOGGER.info("@%s subframes weight are used as is and fixed through all cycles to '%s'"%(self._multiframe,list(weights)))
                subframesWeight = weights
            elif not step%subframesWeight:
                ## CHECK OUT scipy.optimize.minimize TO CREATE ANY TYPE OF CONSTRAINTS
                ## https://mail.python.org/pipermail/tutor/2013-August/097279.html
                framesVector = np.vstack(framesVector)
                weights, r = nnls(framesVector, self._experimentalVector) # non negative least square
                LOGGER.info("@%s subframes weight non negative least square residual is '%s'"%(self._multiframe,r))
                _idx = [idx for idx,c in enumerate(weights) if c!=0]
                if len(_idx) <= 1:
                    _n = normalize if normalize is not None else 1.
                    LOGGER.info("@%s Subframes contribution to total structure are all negligeable except for subframe '%s'. All subrames weight are auto-scaled equally to '%s'"%(self._multiframe, self._subframes[_idx[0]],_n/len(weights)))
                    weights = np.array([_n/len(weights) for _ in weights])
                weights = weights.astype(FLOAT_TYPE)
                # normalize sum of weights to 1
                weights /= np.sum(weights)
            else:
                LOGGER.info("@%s subframes weight not fitted this cycle"%(self._multiframe,))
            ## check for weights drift and divergence
            hasDiverged = False
            if _lastCycleWeigths is not None:
                #hasDiverged = any([(c/p)>2 if c>=p else (c/p)<0.5  for p,c in zip(_lastCycleWeigths, weights)])
                hasDiverged = any([False if p==c==0 else (p/c)<0.5 if c>=p else (c/p)<0.5  for p,c in zip(_lastCycleWeigths, weights)])
            if hasDiverged:
                if _driftTolerance <= 0:
                    LOGGER.error("@%s subframes weight '%s' are diverging. Execution stopped"%(self._multiframe, [(frm,c) for frm,c in zip(self._subframes,weights)]))
                    return
                else:
                    LOGGER.warn("@%s subframes new weight '%s' seems drifting. Using previous values"%(self._multiframe,[(frm,c) for frm,c in zip(self._subframes,weights)]))
                    weights = _lastCycleWeigths
                _driftTolerance -= 1
            else:
                _driftTolerance = driftTolerance
            _lastCycleWeigths = weights
            ## log weights with histogram
            message  = "@%s subframes weight distribution: %s"%(self._multiframe, [(frm,c) for frm,c in zip(self._subframes,weights)],)
            ratio    = 20./max(weights)
            scaled   = [int(math.ceil(c*ratio)) for c in weights]
            bars     = ["%s  %s (%.3f)\n"%('█'*s, f, c) if s>0 else ".  %s (%.3f)\n"%(f,c)for c, s,f in zip(weights, scaled, self._subframes)]
            message  = "%s\n%s"%(message, ''.join(bars))
            LOGGER.info(message)
            ## compute priors and build request dictionary
            request = [{'MODE':'MULTIFRAME_PRIOR', 'multiframePrior':{}, 'multiframeWeight':{}}
                       for _ in self._passwords]
            for cn in self._experimentalCNames:
                tots  = [responseVal[pwd][CN]['total'] for pwd in self._passwords]
                for idx, frm in enumerate(self._passwords):
                    prior = np.array( np.sum([c*t for i,(t,c) in enumerate(zip(tots, weights)) if i!=idx], axis=0), dtype=FLOAT_TYPE )
                    request[idx]['multiframePrior'][cn]  = prior
                    request[idx]['multiframeWeight'][cn] = weights[idx]
            self._orchestrator.transfer_request_to_responder(responder=self._workers,
                                                             password=self._passwords,
                                                             request=request,
                                                             register=True,
                                                             timeout=self._requestTimeout)
            confirmation = self._orchestrator.wait_for_response(password=self._passwords, timeout=self._requestTimeout)
            # check all responses
            _r = [confirmation[frm]['response']['value']=='MULTIFRAME_WEIGHT_AND_PRIOR_UPDATED' if confirmation[pwd] is not None else False for pwd in self._passwords]
            assert all(_r), "All remote subframes didn't confirm updating multiframe weight and prior"
            # save
            if saveFrequency>0:
                if not (step+1)%saveFrequency:
                    _saved = True
                    self.save()
        # final save
        if saveFrequency>0:
            if not _saved:
                self.save()


    def run_independant(self, nCycle=10, numberOfSteps=1000, saveFrequency=1, cycleTimeout=3600):
        """run all remote subframes as totally independant structures

        :Parameters:
           #. nCycle (int): number of total independant cycles
           #. numberOfSteps (int): number of steps per cycle
           #. saveFrequency (int): frequency of saving all frames in between
              cycles
           #. cycleTimeout (None, integer): Estimated time for stochastic
              engine to perform 1 cycle for all frames on remote workers.
              Timeout error will be raise if cycleTimeout is exhausted before
              all workers finish the cycle work.
        """
        assert self.__requesting, "Not ready to request remote workers"
        assert isinstance(numberOfSteps, int), "numberOfSteps must be integer"
        assert numberOfSteps>0, 'numberOfSteps must be >0'
        assert isinstance(saveFrequency, int), 'saveFrequency must be int'
        assert saveFrequency>=0, "saveFrequency must be >=0"
        assert isinstance(nCycle, int), 'nCycle must be int'
        assert nCycle>0, "nCycle must be >0"
        assert isinstance(cycleTimeout, (int, float)), 'cycleTimeout must be a number'
        assert cycleTimeout>=60, "cycleTimeout must be >=60"
        # release all old requests
        self._release_all_requests(onWorkers=False)
        # run ncycles
        for step in range(nCycle):
            LOGGER.info("@%s run_independant cycle %i/%i"%(self._multiframe, step+1,nCycle))
            _saved = False
            # build request
            request=[{'MODE':'RUN_ALL', 'numberOfSteps':numberOfSteps}]*len(self._workers)
            self._orchestrator.transfer_request_to_responder(responder=self._workers,
                                                             password=self._passwords,
                                                             request=request,
                                                             register=True,
                                                             timeout=cycleTimeout)
            responses = self._orchestrator.wait_for_response(password=self._passwords, timeout=cycleTimeout)
            assert all([responses[pwd]['response']['value'] is not None for pwd in self._passwords]), "Timeout retrieving response from executors saving"
            assert all([responses[pwd]['response']['value']=='RUN_ALL_SUCCESSFUL' is not None for pwd in self._passwords]), "Expecting 'RUN_ALL_SUCCESSFUL' as a response"
            self._orchestrator.log_and_transfer('info', "All workers successfully finished running '%s' steps in 'RUN_ALL' mode for '%s'"%(numberOfSteps, self._multiframe))
            # save
            if saveFrequency>0:
                if not (step+1)%saveFrequency:
                    _saved = True
                    self.save()
        # final save
        if saveFrequency>0:
            if not _saved:
                self.save()

    def save(self):
        """Call all remote subFrames to save.
        """
        assert self.__requesting, "Not ready to request remote workers"
        self._orchestrator.transfer_request_to_responder(responder=self._workers,
                                                         password=self._passwords,
                                                         request=['SAVE']*len(self._workers),
                                                         register=True)
        responses = self._orchestrator.wait_for_response(password=self._passwords, timeout=self._requestTimeout)
        assert all([responses[pwd]['response']['value'] is not None for pwd in self._passwords]), "Timeout retrieving response from executors saving"
        assert all([responses[pwd]['response']['value']=='SAVED' is not None for pwd in self._passwords]), "Expecting 'SAVED' as a response"
        self._orchestrator.log_and_transfer('info', "All workers successfully save engine for frame '%s'"%(self._multiframe))



    def _on_worker(self, executor, userGun, password, engineFilePath, frame, requestLoopTimeout=3600):
        ### set parameters
        self._executor           = executor
        self._userGun            = userGun
        self._password           = password
        self._frame              = frame
        self._engineFilePath     = engineFilePath
        self._requestLoopTimeout = requestLoopTimeout
        ## import fullrmc and load engine
        try:
            from fullrmc.Engine import Engine
            from fullrmc.Core.Constraint import ExperimentalConstraint
            from fullrmc.Constraints.PairDistributionConstraints import PairDistributionConstraint
            from fullrmc.Constraints.StructureFactorConstraints import StructureFactorConstraint
        except Exception as err:
            err = 'Unable to import fullrmc Engine (%s)'%str(err)
            self._executor.log_and_transfer('error', err)
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request='ERROR: %s'%err,
                                                         register=False,
                                                         errorRaise=True,
                                                         errorLog=True)
            return
        ## load engine
        try:
            self._engine = Engine(path=None, timeout=self._repoTimeout).load(self._engineFilePath, safeMode=False)
            self._engine._Engine__set_runtime_ncores(1) # allow single core running for remote fullrmc
        except Exception as err:
            err = 'Unable to import fullrmc Engine (%s)'%str(err)
            self._executor.log_and_transfer('error', err)
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request='ERROR: %s'%err,
                                                         register=False,
                                                         errorRaise=True,
                                                         errorLog=True)
            return
        else:
            self._executor.log_and_transfer('info', 'Stochastic engine (@path: %s) is successfully loaded'%self._engineFilePath)
        ## set used frame
        try:
            isNormalFrame, isMultiframe, isSubframe = self._engine.get_frame_category(self._frame)
            assert isSubframe, "Remote fullrmc frame must be a subframe, '%s' is given instead"%(self._frame)
            self._engine.set_used_frame(frame=self._frame, _updateRepo=False)
        except Exception as err:
            err = 'Unable to set engine used frame (%s)'%str(err)
            self._executor.log_and_transfer('error', err)
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request='ERROR: %s'%err,
                                                         register=False,
                                                         errorRaise=True,
                                                         errorLog=True)
            return
        ## get and initialize used constraints
        try:
            self._usedConstraints, self._constraints, self._rigidConstraints = self._engine.initialize_used_constraints(sortConstraints=True)
            if not len(self._usedConstraints):
                self._executor.log_and_transfer(logType='warn', message="@%s No constraints are used. Configuration will be randomized"%self._frame)
            # runtime initialize group selector
            self._engine._Engine__groupSelector._runtime_initialize()
            # runtime initialize constraints
            [c._runtime_initialize() for c in self._usedConstraints]
            # compute totalStandardError
            self._engine._Engine__totalStandardError = self._engine.compute_total_standard_error(self._constraints, current="standardError")
        except Exception as err:
            err = 'Unable to initialize stochastic engine (%s)'%str(err)
            self._executor.log_and_transfer('error', err)
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request='ERROR: %s'%err,
                                                         register=False,
                                                         errorRaise=True,
                                                         errorLog=True)
            return
        ## get experimental constraints information
        try:
            self._experimentalConstraints = [c for c in self._usedConstraints if isinstance(c, ExperimentalConstraint)]
            self._experimentalConstInfo   = {'scipy_nnls_available': nnls is not None}
            for c in self._experimentalConstraints:
                cname = c.constraintName
                assert cname not in self._experimentalConstInfo, "constraint name exists, this shouldn't have happened. PLEASE REPORT"
                if isinstance(c, PairDistributionConstraint):
                    self._experimentalConstInfo[cname] = {'minimumDistance' :c.minimumDistance,
                                                          'maximumDistance' :c.maximumDistance,
                                                          'bin'             :c.bin,
                                                          '_expData'        :c.experimentalPDF}
                elif isinstance(c, StructureFactorConstraint):
                    self._experimentalConstInfo[cname] = {'qmin'     :c.qmin,
                                                          'qmax'     :c.qmax,
                                                          'dq'       :c.dq,
                                                          '_expData' :c.experimentalSF}
                else:
                    raise Exception("experimental constraint '%s' is not known to run on remote machines"%c.constraintName)
        except Exception as err:
            err = 'Unable to get experimental data information (%s)'%str(err)
            self._executor.log_and_transfer('error', err)
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request='ERROR: %s'%err,
                                                         register=False,
                                                         errorRaise=True,
                                                         errorLog=True)
            return
        ## send experimental data information request to user executor
        try:
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request={'EXPERIMENTAL_CONSTRAINT_INFO':self._experimentalConstInfo},
                                                         register=True,
                                                         errorRaise=True,
                                                         errorLog=True)
            response = self._executor.wait_for_response(password=self._password, timeout=self._requestTimeout, frequency=0.0005)
            assert self._password in response, "retrieved response password is missing. PLEASE REPORT"
            assert response[self._password] is not None, "retrieved response is empty. Maybe timeout has expired"
            assert response[self._password]['response'] is not None, "retrieved response is empty. Maybe timeout has expired"
            self._allowedModes = response[self._password]['response']['value']
        except Exception as err:
            err = 'Unable to get experimental data information (%s)'%str(err)
            self._executor.log_and_transfer('error', err)
            self._executor.transfer_request_to_responder(responder=self._userGun,
                                                         password=self._password,
                                                         request='ERROR: %s'%err,
                                                         register=False,
                                                         errorRaise=True,
                                                         errorLog=True)
            return
        ## start launch request loop
        self.__launch_requests_loop()


    def __launch_requests_loop(self):
        _lastSavedTotalStandardError = self._engine.totalStandardError
        _coordsBeforeMove            = None
        _moveTried                   = False
        _rejectMove                  = False
        _rejectRemove                = False
        _movedRealCoordinates        = None
        _movedBoxCoordinates         = None
        _usedConstraints             = self._usedConstraints
        _constraints                 = self._constraints
        _rigidConstraints            = self._rigidConstraints
        # log engine state
        self._executor.log_and_transfer('info', 'Stochastic engine @%s (Std. Err. %s) ready for requests of type %s. Maximum idle time is %s'%(self._frame, self._engine.totalStandardError,self._allowedModes, self._requestLoopTimeout))
        #   #####################################################################################   #
        #   ############################# RUN REQUEST RESPONSE LOOP #############################   #
        while not self._executor._killSignal:
            request = self._executor.wait_for_request(password=self._password, timeout=self._requestLoopTimeout, frequency=0.0005)
            # get request value
            assert self._password in request, "retrieved request password is missing. PLEASE REPORT"
            if request[self._password] is None:
                value     = 'REQUEST_TIMEOUT'
            else:
                value     = request[self._password]['request']
                requester = request[self._password]['requester']
            # check for request to break
            if isinstance(value, basestring):
                if value == 'REQUEST_TIMEOUT':
                    message = "Engine @%s no request recieved in '%s' return gracefully"%(self._engine.usedFrame,self._requestLoopTimeout)
                    self._executor.log_and_transfer('timeout', message)
                    LOGGER.info( message )
                    return
                elif str(value) == 'STOP':
                    message = "Engine @%s listening to user's requests STOPPED"%self._engine.usedFrame
                    LOGGER.info(message)
                    self._executor.log_and_transfer('info', message)
                    self._executor.transfer_response_to_requester(requester=requester,
                                                                  password=self._password,
                                                                  response='STOPPED',
                                                                  errorRaise=True,
                                                                  errorLog=True)
                    return
                elif str(value) == 'SAVE':
                    _lastSavedTotalStandardError = \
                    self._engine._Engine__on_runtime_step_save_engine(_saveFrequency               = 1,
                                                                      step                         = 1,
                                                                      _frame                       = self._frame,
                                                                      _usedConstraints             = _usedConstraints,
                                                                      _lastSavedTotalStandardError = _lastSavedTotalStandardError)
                    self._executor.transfer_response_to_requester(requester=requester,
                                                                  password=self._password,
                                                                  response='SAVED',
                                                                  errorRaise=True,
                                                                  errorLog=True)
                    continue
                else:
                    raise Exception("String request value '%s' is not known"%value)
            else:
                assert isinstance(value,dict), "request must be string or dict"
                mode = value.get('MODE', None)
                assert mode is not None, "request dict 'MODE' is not given. %s keys are given instead"%list(value)
                assert mode in self._allowedModes, "requested mode is not allowed"
                # update multiframe prior parameters
                if mode == 'MULTIFRAME_PRIOR':
                    multiframePrior  = value['multiframePrior']
                    multiframeWeight = value['multiframeWeight']
                    for c in self._experimentalConstraints:
                        cn = c.constraintName
                        assert cn in multiframePrior,  "experimental constraint '%s' multiframePrior is missing"%(cn)
                        assert cn in multiframeWeight, "experimental constraint '%s' multiframeWeight is missing"%(cn)
                        c._ExperimentalConstraint__multiframePrior  = value['multiframePrior'][cn]
                        c._ExperimentalConstraint__multiframeWeight = value['multiframeWeight'][cn]
                    # recompute constraints standard error
                    ## MUST RECOMPUTE CONSTRAINTS STANDARD ERROR
                    for c in self._constraints:
                        c.update_standard_error()
                    # re-compute standard error
                    self._engine._Engine__totalStandardError = self._engine.compute_total_standard_error(self._constraints, current="standardError")
                    # respond back
                    self._executor.transfer_response_to_requester(requester=requester,
                                                                  password=self._password,
                                                                  response='MULTIFRAME_WEIGHT_AND_PRIOR_UPDATED',
                                                                  errorRaise=True,
                                                                  errorLog=True)
                    continue
                # run modes
                elif mode in ('FIRST_ACCEPTED', 'RUN_ALL'):
                    numberOfSteps = value.get('numberOfSteps', None)
                    assert numberOfSteps is not None, "request dict 'numberOfSteps' is not given. %s keys are given instead"%list(value)
                    assert isinstance(numberOfSteps, int), "numberOfSteps must be integer"
                    assert numberOfSteps > 10, "numberOfSteps must be at least 10"
                    if mode == 'FIRST_ACCEPTED':
                        firstNAccepted = value.get('firstNAccepted', None)
                        assert firstNAccepted is not None, "request dict 'firstNAccepted' is not given. %s keys are given instead"%list(value)
                        assert isinstance(firstNAccepted, int), "firstNAccepted must be integer"
                        assert firstNAccepted>0, "firstNAccepted must be >0"
                    else:
                        firstNAccepted = numberOfSteps+1
                    #   #####################################################################################   #
                    #   #################################### RUN ENGINE #####################################   #
                    acceptedAtStart = self._engine._Engine__accepted
                    for step in xrange(numberOfSteps):
                        ## constraint runtime_on_step
                        [c._runtime_on_step() for c in _usedConstraints]
                        ## increment generated
                        self._engine._Engine__generated += 1
                        ## get selected indexes and coordinates
                        _coordsBeforeMove,     \
                        _movedRealCoordinates, \
                        _movedBoxCoordinates = \
                        self._engine._Engine__on_runtime_step_select_group(_coordsBeforeMove     = _coordsBeforeMove,
                                                                           _movedRealCoordinates = _movedRealCoordinates,
                                                                           _moveTried            = _moveTried)
                        if not len(self._engine._RT_groupAtomsIndexes):
                            LOGGER.nottried("@%s Generated move %i can't be tried because all atoms are collected."%(self._engine.usedFrame,self._engine._Engine__generated))
                        else:
                            # try move atom
                            if _movedRealCoordinates is None:
                                _moveTried, _rejectRemove = self._engine._Engine__on_runtime_step_try_remove(_constraints      = _constraints,
                                                                                                             _rigidConstraints = _rigidConstraints,
                                                                                                             _usedConstraints  = _usedConstraints)
                            # try remove atom
                            else:
                                _moveTried, _rejectMove = self._engine._Engine__on_runtime_step_try_move(_constraints          = _constraints,
                                                                                                         _rigidConstraints     = _rigidConstraints,
                                                                                                         _usedConstraints      = _usedConstraints,
                                                                                                         _movedRealCoordinates = _movedRealCoordinates,
                                                                                                         _movedBoxCoordinates  = _movedBoxCoordinates)
                        # check if step accepted and break
                        if self._engine._Engine__accepted-acceptedAtStart>=firstNAccepted:
                            break
                else:
                    raise Exception("unkown given run mode '%s'"%mode)
                ## respond
                if mode == 'RUN_ALL':
                    response = "RUN_ALL_SUCCESSFUL"
                else:
                    ## ALWAYS RETURN TOTALS WITHOUT APPLYING MULTIFRAME PRIOR.
                    response = [(c, c.get_constraint_value(applyMultiframePrior=False)) for c in self._experimentalConstraints]
                    response = [(c.constraintName, {'total':d.get('total',None), 'weight':c.multiframeWeight}) for c,d in response]
                    response = dict(response)
                self._executor.transfer_response_to_requester(requester=requester,
                                                              password=self._password,
                                                              response=response,
                                                              errorRaise=True,
                                                              errorLog=True)
