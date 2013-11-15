# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Category.gender'
        db.alter_column('pingpong_category', 'gender', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):

        # Changing field 'Category.gender'
        db.alter_column('pingpong_category', 'gender', self.gf('django.db.models.fields.IntegerField')(default=0))

    models = {
        'bracket.bracket': {
            'Meta': {'object_name': 'Bracket'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pingpong.Category']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'bracket.bracketslot': {
            'Meta': {'object_name': 'BracketSlot'},
            'bracket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bracket.Bracket']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'loser_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'loser_set'", 'null': 'True', 'to': "orm['bracket.BracketSlot']"}),
            'match_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'match_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'no_player': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pingpong.Player']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pingpong.Table']", 'null': 'True', 'blank': 'True'}),
            'winner_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'winner_set'", 'null': 'True', 'to': "orm['bracket.BracketSlot']"})
        },
        'group.group': {
            'Meta': {'object_name': 'Group'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pingpong.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pingpong.Table']", 'null': 'True', 'blank': 'True'})
        },
        'pingpong.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'pingpong.match': {
            'Meta': {'object_name': 'Match'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['group.Group']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['pingpong.Player']"}),
            'player1_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['bracket.BracketSlot']"}),
            'player1_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['pingpong.Player']"}),
            'player2_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['bracket.BracketSlot']"}),
            'player2_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_matches'", 'null': 'True', 'to': "orm['pingpong.Table']"})
        },
        'pingpong.player': {
            'Meta': {'object_name': 'Player'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'players'", 'null': 'True', 'to': "orm['pingpong.Category']"}),
            'club': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pingpong.table': {
            'Meta': {'object_name': 'Table'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pingpong']