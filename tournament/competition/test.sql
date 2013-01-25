SELECT
  "competition_bracketslot"."id",
  COUNT(T5."id") AS "s2c",
  COUNT(T8."id") AS "s3c"
FROM "competition_bracketslot"
  INNER JOIN "competition_bracket" ON ("competition_bracketslot"."bracket_id" = "competition_bracket"."id")
  INNER JOIN "registration_category" ON ("competition_bracket"."category_id" = "registration_category"."id")
  LEFT OUTER JOIN "competition_bracketslot" T4
    ON ("competition_bracketslot"."winner_goes_to_id" = T4."id")
  LEFT OUTER JOIN "competition_bracketslot" T5
    ON (T4."id" = T5."winner_goes_to_id")
  LEFT OUTER JOIN "registration_player" ON (T5."player_id" = "registration_player"."id")
  LEFT OUTER JOIN "registration_player" T7
    ON ("registration_player"."id" = T7."part_of_double_id")
  LEFT OUTER JOIN "competition_bracketslot" T8
    ON (T7."id" = T8."player_id")
WHERE ("competition_bracketslot"."status" = 0 AND "registration_category"."gender" >= 2 AND T8."status" < 2)
GROUP BY "competition_bracketslot"."id"
HAVING (COUNT(T5."id") = 4 AND COUNT(T8."id") = 0);
args = (0, 2, 2, 4, 0)

SELECT
  s.*
FROM competition_bracketslot s
  INNER JOIN competition_bracket b
    ON b.id = s.bracket_id
  INNER JOIN registration_category c
    ON c.id = b.category_id
  INNER JOIN competition_bracketslot s2
    ON s2.winner_goes_to_id = s.winner_goes_to_id
  INNER JOIN registration_player p
    ON p.id = s2.player_id
  INNER JOIN registration_player p2
    ON p2.part_of_double_id = p.id
  LEFT JOIN competition_bracketslot s3
    ON s3.player_id = p2.id AND s3.status < 2
WHERE c.gender >= 2
      AND s.status = %s
GROUP BY s.id
HAVING COUNT(s2.id) = 4
AND COUNT(s3.id) = 0
