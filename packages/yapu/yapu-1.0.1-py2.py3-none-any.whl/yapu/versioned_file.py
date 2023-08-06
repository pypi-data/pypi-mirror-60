
from ..imports.internal   import *


class VersionedOutputFile:
    """ 
    Like a file object opened for output, but with versioned backups
    of anything it might otherwise overwrite 
    
    #https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s27.html
    """

    def __init__(self, pathname, numSavedVersions=3):
        """ Create a new output file. pathname is the name of the file to 
        [over]write. numSavedVersions tells how many of the most recent
        versions of pathname to save. """
        self._pathname = pathname
        self._tmpPathname = "%s.~new~" % self._pathname
        self._numSavedVersions = numSavedVersions
        self._outf = open(self._tmpPathname, "w")   # use "wb" and str.encode() for better compatibility.

    def __del__(self):
        self.close(  )

    def close(self):
        if self._outf:
            self._outf.close(  )
            self._replaceCurrentFile(  )
            self._outf = None

    def asFile(self):
        """ Return self's shadowed file object, since marshal is
        pretty insistent on working with real file objects. """
        return self._outf

    def __getattr__(self, attr):
        """ Delegate most operations to self's open file object. """
        return getattr(self._outf, attr)

    def _replaceCurrentFile(self):
        """ Replace the current contents of self's named file. """
        self._backupCurrentFile(  )
        os.rename(self._tmpPathname, self._pathname)

    def _backupCurrentFile(self):
        """ Save a numbered backup of self's named file. """
        # If the file doesn't already exist, there's nothing to do
        if os.path.isfile(self._pathname):
            newName = self._versionedName(self._currentRevision(  ) + 1)
            os.rename(self._pathname, newName)

            # Maybe get rid of old versions
            if ((self._numSavedVersions is not None) and
                (self._numSavedVersions > 0)):
                self._deleteOldRevisions(  )

    def _versionedName(self, revision):
        """ Get self's pathname with a revision number appended. """
        return "%s.~%s~" % (self._pathname, revision)

    def _currentRevision(self):
        """ Get the revision number of self's largest existing backup. """
        revisions = [0] + self._revisions(  )
        return max(revisions)

    def _revisions(self):
        """ Get the revision numbers of all of self's backups. """
        revisions = []
        backupNames = glob.glob("%s.~[0-9]*~" % (self._pathname))
        for name in backupNames:
            try:
                revision = int(str.split(name, "~")[-2])
                revisions.append(revision)
            except ValueError:
                # Some ~[0-9]*~ extensions may not be wholly numeric
                pass
        revisions.sort(  )
        return revisions

    def _deleteOldRevisions(self):
        """ Delete old versions of self's file, so that at most
        self._numSavedVersions versions are retained. """
        revisions = self._revisions(  )
        revisionsToDelete = revisions[:-self._numSavedVersions]
        for revision in revisionsToDelete:
            pathname = self._versionedName(revision)
            if os.path.isfile(pathname):
                os.remove(pathname)

                