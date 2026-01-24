from axis1.schema import Axis1Card, Axis1Face, Axis1Characteristics, Axis1Metadata, Axis1SearchIndex

class Axis1Mapper:
    def map(self, scry: dict) -> Axis1Card:

        # ------------------------------------------------------------
        # 1. Handle multi-face cards (modal_dfc, transform, split, adventure)
        # ------------------------------------------------------------
        faces = []
        if "card_faces" in scry and scry["card_faces"]:
            for idx, f in enumerate(scry["card_faces"]):
                type_line = f.get("type_line", "")
                if "—" in type_line:
                    types_part, subtypes_part = [p.strip() for p in type_line.split("—", 1)]
                    card_types = types_part.split()
                    subtypes = subtypes_part.split()
                else:
                    card_types = type_line.split()
                    subtypes = []

                oracle_text = f.get("oracle_text")
                flavor_text = f.get("flavor_text")

                face = Axis1Face(
                    face_id=f"face_{idx}",
                    name=f.get("name"),
                    type_line=type_line or None,
                    mana_cost=f.get("mana_cost"),
                    mana_value=f.get("cmc", scry.get("cmc")),
                    colors=f.get("colors", []),
                    color_indicator=f.get("color_indicator") or [],
                    card_types=card_types,
                    supertypes=[t for t in card_types if t in ["Legendary", "Basic", "Snow", "World", "Ongoing"]],
                    subtypes=subtypes,
                    power=f.get("power"),
                    toughness=f.get("toughness"),
                    loyalty=f.get("loyalty"),
                    defense=f.get("defense"),
                    oracle_text=oracle_text,
                    printed_text=f.get("printed_text"),
                    flavor_text=flavor_text,
                    image_uris=f.get("image_uris") or {},
                    keywords=f.get("keywords", []),
                    produced_mana=f.get("produced_mana") or scry.get("produced_mana") or [],
                )
                faces.append(face)

            # Use the *front face* for characteristics
            front = faces[0]
            card_types = front.card_types
            subtypes = front.subtypes

        else:
            # ------------------------------------------------------------
            # 2. Normal single-face card
            # ------------------------------------------------------------
            type_line = scry.get("type_line", "")
            if "—" in type_line:
                types_part, subtypes_part = [p.strip() for p in type_line.split("—", 1)]
                card_types = types_part.split()
                subtypes = subtypes_part.split()
            else:
                card_types = type_line.split()
                subtypes = []

            oracle_text = scry.get("oracle_text")
            flavor_text = scry.get("flavor_text")

            face = Axis1Face(
                face_id="front",
                name=scry["name"],
                type_line=type_line or None,
                mana_cost=scry.get("mana_cost"),
                mana_value=scry.get("cmc"),
                colors=scry.get("colors", []),
                color_indicator=scry.get("color_indicator") or [],
                card_types=card_types,
                supertypes=[t for t in card_types if t in ["Legendary", "Basic", "Snow", "World", "Ongoing"]],
                subtypes=subtypes,
                power=scry.get("power"),
                toughness=scry.get("toughness"),
                loyalty=scry.get("loyalty"),
                defense=scry.get("defense"),
                oracle_text=oracle_text,
                printed_text=scry.get("printed_text"),
                flavor_text=flavor_text,
                image_uris=scry.get("image_uris") or {},
                keywords=scry.get("keywords", []),
                produced_mana=scry.get("produced_mana") or [],
            )
            faces = [face]

        # ------------------------------------------------------------
        # 3. Characteristics (based on front face)
        # ------------------------------------------------------------
        characteristics = Axis1Characteristics(
            mana_cost=faces[0].mana_cost,
            mana_value=faces[0].mana_value,
            type_line=faces[0].type_line or scry.get("type_line"),
            colors=faces[0].colors,
            color_identity=scry.get("color_identity", []),
            color_indicator=faces[0].color_indicator,
            card_types=faces[0].card_types,
            supertypes=faces[0].supertypes,
            subtypes=faces[0].subtypes,
            power=faces[0].power,
            toughness=faces[0].toughness,
            loyalty=faces[0].loyalty,
            defense=faces[0].defense,
        )

        # ------------------------------------------------------------
        # 4. Metadata
        # ------------------------------------------------------------
        # Capture prices from Scryfall (can be None for some currencies)
        prices = scry.get("prices") or {}
        # Ensure prices dict is properly formatted
        prices_dict = {}
        if prices:
            for key, value in prices.items():
                prices_dict[key] = value  # Can be None or string
        
        metadata = Axis1Metadata(
            rarity=scry.get("rarity"),
            artist=scry.get("artist"),
            illustration_id=scry.get("illustration_id"),
            frame=scry.get("frame"),
            border_color=scry.get("border_color"),
            watermark=scry.get("watermark"),
            set_name=scry.get("set_name"),
            set_type=scry.get("set_type"),
            released_at=scry.get("released_at"),
            reserved=scry.get("reserved"),
            digital=scry.get("digital"),
            promo=scry.get("promo"),
            reprint=scry.get("reprint"),
            variation=scry.get("variation"),
            full_art=scry.get("full_art"),
            oversized=scry.get("oversized"),
            foil=scry.get("foil"),
            nonfoil=scry.get("nonfoil"),
            finishes=scry.get("finishes") or [],
            games=scry.get("games") or [],
            security_stamp=scry.get("security_stamp"),
            legalities=scry.get("legalities") or {},
            image_uris=scry.get("image_uris") or {},
            prices=prices_dict,
        )

        search_index = Axis1SearchIndex(
            name=scry.get("name"),
            names=[f.name for f in faces],
            type_line=scry.get("type_line") or faces[0].type_line,
            colors=scry.get("colors") or faces[0].colors,
            color_identity=scry.get("color_identity", []),
            card_types=faces[0].card_types,
            supertypes=faces[0].supertypes,
            subtypes=faces[0].subtypes,
            keywords=scry.get("keywords", []),
            produced_mana=scry.get("produced_mana") or [],
            mana_value=scry.get("cmc"),
            power=faces[0].power,
            toughness=faces[0].toughness,
            loyalty=faces[0].loyalty,
            defense=faces[0].defense,
            rarity=scry.get("rarity"),
            set_code=scry.get("set"),
            set_name=scry.get("set_name"),
            set_type=scry.get("set_type"),
            layout=scry.get("layout", "normal"),
            released_at=scry.get("released_at"),
            oracle_text=scry.get("oracle_text") or faces[0].oracle_text,
        )

        # ------------------------------------------------------------
        # 5. Build Axis1Card
        # ------------------------------------------------------------
        axis1 = Axis1Card(
            card_id=scry["id"],
            oracle_id=scry.get("oracle_id"),
            scryfall_id=scry.get("id"),
            set=scry.get("set"),
            set_name=scry.get("set_name"),
            set_type=scry.get("set_type"),
            collector_number=scry.get("collector_number"),
            lang=scry.get("lang"),
            layout=scry.get("layout", "normal"),
            object_kind="card",
            name=scry.get("name"),
            names=[f.name for f in faces],
            printed_name=scry.get("printed_name", faces[0].name),
            type_line=scry.get("type_line") or faces[0].type_line,
            oracle_text=scry.get("oracle_text") or faces[0].oracle_text,
            mana_cost=scry.get("mana_cost"),
            mana_value=scry.get("cmc"),
            colors=scry.get("colors") or faces[0].colors,
            color_identity=scry.get("color_identity", []),
            keywords=scry.get("keywords", []),
            produced_mana=scry.get("produced_mana") or [],
            power=faces[0].power,
            toughness=faces[0].toughness,
            loyalty=faces[0].loyalty,
            defense=faces[0].defense,
            released_at=scry.get("released_at"),
            faces=faces,
            characteristics=characteristics,
            intrinsic_rules=[],
            intrinsic_limits=[],
            intrinsic_counters=[],
            characteristic_sources={},
            rules_tags=[],
            metadata=metadata,
            search_index=search_index,
        )

        return axis1
