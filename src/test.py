import forecastio


byHour = forecast.currently()
print byHour.summary
print byHour.icon
print byHour.temperature