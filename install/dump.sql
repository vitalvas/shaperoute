CREATE TABLE `admins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `passwd` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `acl_full` enum('true','false') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'false',
  `realname` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `active` enum('true','false') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'true',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `channels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `table` int(3) NOT NULL,
  `fib` int(2) NOT NULL DEFAULT '0',
  `active` enum('true','false') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'false',
  `gateway` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `networks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(20) NOT NULL,
  `comment` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
CREATE TABLE `pipes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL,
  `pipe_in` int(11) NOT NULL,
  `pipe_out` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `network` varchar(20) NOT NULL,
  `comment` varchar(200) NOT NULL,
  `status` enum('true','false') NOT NULL DEFAULT 'false',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `realname` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `groups` int(11) NOT NULL,
  `ip` varchar(17) COLLATE utf8_unicode_ci NOT NULL,
  `mac` varchar(17) COLLATE utf8_unicode_ci NOT NULL,
  `active` enum('true','false') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'false',
  `limit_sites` enum('true','false') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'false',
  `channel` int(11) NOT NULL DEFAULT '1',
  `bw_up` int(11) NOT NULL DEFAULT '1024',
  `bw_down` int(11) NOT NULL DEFAULT '1024',
  `comment` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `users_grp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `active` enum('true','false') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'true',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `users_full` AS select inet_aton(`users`.`ip`) AS `sort_ip`,`users`.`id` AS `id`,`users`.`username` AS `username`,`users`.`realname` AS `realname`,`users`.`ip` AS `ip`,`users`.`mac` AS `mac`,`users`.`active` AS `active`,`users`.`limit_sites` AS `limit_sites`,`users`.`bw_up` AS `bw_up`,`users`.`bw_down` AS `bw_down`,`users_grp`.`name` AS `grp`,`users`.`groups` AS `groups`,`channels`.`name` AS `channel` from ((`users` left join `users_grp` on((`users`.`groups` = `users_grp`.`id`))) left join `channels` on((`users`.`channel` = `channels`.`id`))) order by inet_aton(`users`.`ip`);
