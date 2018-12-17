# -*- coding: utf-8 -*-
from flask import Blueprint

from . import controllers

mme_bp = Blueprint('matchmaker', __name__)

@mme_bp.route('/matchmaker/update', methods=['POST'])
def matchmaker_add():
    """Takes care of adding/updating patients in scout MatchMaker"""
    return 'Adding/updating shit here!'


@mme_bp.route('/matchmaker/delete', methods=['DELETE', 'GET'])
def matchmaker_delete():
    """Takes care of removing patients from Scout MatchMaker"""
    return 'Removing patients here'


@mme_bp.route('/matchmaker/match', methods=['POST', 'GET'])
def matchmaker_match():
    """Takes care of internal/external patient matching"""
    return "matching patients here!"
