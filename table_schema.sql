# ************************************************************
# Sequel Pro SQL dump
# Version 4096
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: 127.0.0.1 (MySQL 5.6.14)
# Database: travel
# Generation Time: 2013-12-30 19:39:03 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table cities
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cities`;

CREATE TABLE `cities` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `address` varchar(255) NOT NULL DEFAULT '',
  `summary` text,
  `latitude` varchar(50) NOT NULL DEFAULT '',
  `longitude` varchar(50) NOT NULL DEFAULT '',
  `country` varchar(3) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`,`latitude`,`longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table cities_books
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cities_books`;

CREATE TABLE `cities_books` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `thumbnail` varchar(255) NOT NULL DEFAULT '',
  `url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table cities_events
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cities_events`;

CREATE TABLE `cities_events` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `eventbrite_id` varchar(255) NOT NULL DEFAULT '',
  `title` varchar(255) NOT NULL DEFAULT '',
  `url` varchar(255) NOT NULL DEFAULT '',
  `logo` varchar(255) DEFAULT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `venue_latitude` varchar(50) NOT NULL DEFAULT '',
  `venue_longitude` varchar(50) NOT NULL DEFAULT '',
  `venue_address` varchar(100) DEFAULT NULL,
  `venue_address_2` varchar(100) DEFAULT NULL,
  `venue_name` varchar(255) NOT NULL DEFAULT '',
  `organizer_name` varchar(255) NOT NULL DEFAULT '',
  `organizer_url` varchar(255) DEFAULT NULL,
  `repeats` tinyint(1) NOT NULL DEFAULT '0',
  `repeat_schedule` text,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `eventbrite_id` (`eventbrite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table cities_hotels
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cities_hotels`;

CREATE TABLE `cities_hotels` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `hotel_id` varchar(30) NOT NULL,
  `name` varchar(255) NOT NULL DEFAULT '',
  `thumbnail` varchar(255) DEFAULT NULL,
  `description` varchar(500) NOT NULL DEFAULT '',
  `location_description` varchar(255) NOT NULL DEFAULT '',
  `url` varchar(512) NOT NULL DEFAULT '',
  `latitude` varchar(50) NOT NULL DEFAULT '',
  `longitude` varchar(50) NOT NULL DEFAULT '',
  `address` varchar(255) NOT NULL DEFAULT '',
  `low_rate` varchar(20) NOT NULL DEFAULT '',
  `high_rate` varchar(20) NOT NULL DEFAULT '',
  `rating` varchar(3) NOT NULL DEFAULT '',
  `trip_advisor_rating` varchar(3) DEFAULT NULL,
  `amenity_mask` varchar(30) DEFAULT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table cities_videos
# ------------------------------------------------------------

DROP TABLE IF EXISTS `cities_videos`;

CREATE TABLE `cities_videos` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `video_id` varchar(32) NOT NULL DEFAULT '',
  `title` varchar(255) NOT NULL DEFAULT '',
  `thumbnail` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table hotels_photos
# ------------------------------------------------------------

DROP TABLE IF EXISTS `hotels_photos`;

CREATE TABLE `hotels_photos` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `hotel_id` int(11) NOT NULL,
  `expedia_hotel_id` varchar(30) NOT NULL DEFAULT '',
  `url` varchar(512) NOT NULL DEFAULT '',
  `is_large` tinyint(1) NOT NULL DEFAULT '0',
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table photos
# ------------------------------------------------------------

DROP TABLE IF EXISTS `photos`;

CREATE TABLE `photos` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `size` varchar(30) NOT NULL DEFAULT '',
  `url` varchar(255) NOT NULL DEFAULT '',
  `width` int(5) NOT NULL,
  `height` int(5) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table places
# ------------------------------------------------------------

DROP TABLE IF EXISTS `places`;

CREATE TABLE `places` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `gapi_id` varchar(255) NOT NULL,
  `city_id` int(11) unsigned NOT NULL,
  `reference` varchar(512) NOT NULL DEFAULT '',
  `types` varchar(255) NOT NULL DEFAULT '',
  `name` varchar(255) NOT NULL DEFAULT '',
  `vicinity` varchar(255) DEFAULT '',
  `latitude` varchar(50) NOT NULL DEFAULT '',
  `longitude` varchar(50) NOT NULL DEFAULT '',
  `rating` float DEFAULT NULL,
  `icon` varchar(255) NOT NULL DEFAULT '',
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gapi_id` (`gapi_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table places_events
# ------------------------------------------------------------

DROP TABLE IF EXISTS `places_events`;

CREATE TABLE `places_events` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `place_id` int(11) NOT NULL,
  `event_id` varchar(255) NOT NULL DEFAULT '',
  `start_time` datetime NOT NULL,
  `summary` text NOT NULL,
  `url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table places_photos
# ------------------------------------------------------------

DROP TABLE IF EXISTS `places_photos`;

CREATE TABLE `places_photos` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `place_id` int(11) NOT NULL,
  `reference` varchar(512) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table places_reviews
# ------------------------------------------------------------

DROP TABLE IF EXISTS `places_reviews`;

CREATE TABLE `places_reviews` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `place_id` int(11) NOT NULL,
  `author_id` varchar(255) NOT NULL DEFAULT '',
  `author_name` varchar(255) NOT NULL DEFAULT '',
  `review` text NOT NULL,
  `aspects` varchar(1000) DEFAULT '',
  `rating` float NOT NULL,
  `reviewed_on` datetime NOT NULL,
  `has_photo` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table plans
# ------------------------------------------------------------

DROP TABLE IF EXISTS `plans`;

CREATE TABLE `plans` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `city_id` int(11) NOT NULL,
  `types` varchar(255) DEFAULT NULL,
  `events` varchar(255) DEFAULT NULL,
  `status` tinyint(1) DEFAULT '0',
  `completed_tasks` int(5) NOT NULL DEFAULT '0',
  `total_tasks` int(5) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table plans_forecast
# ------------------------------------------------------------

DROP TABLE IF EXISTS `plans_forecast`;

CREATE TABLE `plans_forecast` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `plan_id` int(11) NOT NULL,
  `future_day` int(11) NOT NULL,
  `summary` varchar(255) DEFAULT NULL,
  `offset` tinyint(3) NOT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `hourly_data` longtext NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `plan_id` (`plan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table users
# ------------------------------------------------------------

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `display_name` varchar(255) DEFAULT '',
  `avatar` varchar(512) DEFAULT '',
  `profile_url` varchar(512) DEFAULT NULL,
  `google_id` varchar(255) NOT NULL DEFAULT '',
  `access_token` varchar(512) NOT NULL DEFAULT '',
  `id_token` varchar(2048) NOT NULL DEFAULT '',
  `email` varchar(255) DEFAULT NULL,
  `expires_at` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `google_id` (`google_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
