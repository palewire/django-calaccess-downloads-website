node[:crons].each_pair do |cronname, options|
    cron cronname do
      minute options[:minute] || "*"
      hour options[:hour] || "*"
      day options[:day] || "*"
      month options[:month] || "*"
      weekday options[:weekday] || "*"
      user options[:user] || node[:app][:user]
      shell '/bin/bash'
      command options[:command]
    end
end

