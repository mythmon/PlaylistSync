class CacheVersionError(Exception):
	def __init__(self, versionFound, versionExpected):
		self.versionFound = versionFound
		self.versionExpected = versionExpected

	def __str__(self):
		return "Expected cache version {0}, found cache version {1}.".format(
			self.versionFound, self.versionExpected)
