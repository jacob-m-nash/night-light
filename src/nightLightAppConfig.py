from json import JSONEncoder, dump
from pathlib import Path
class NightLightAppConfig():
    def __init__(self,nightLightConfigPath = "configs/defaultNightLightConfig.json",nightLightLogsPath = "logs/nightLightLogs.log"):
        self.nightLightConfig = nightLightConfigPath
        self.nightLightLogs = nightLightLogsPath
    
    def GenerateDefaultConfig(configFile: Path) -> str:
         try:
            configFile.parent.mkdir(parents=True, exist_ok=True)
            config = NightLightAppConfig()
            with open(configFile, 'w') as f:
                   dump(config,f, indent=4, sort_keys=True,cls=NightLightAppConfigEncoder)
            return configFile
         except Exception as e:
              raise Exception(f"Failed to generate default app config at {configFile}") from e
              
             
class NightLightAppConfigEncoder(JSONEncoder):
    def default(self, o):
            return o.__dict__
